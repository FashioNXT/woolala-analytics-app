from flask import current_app
import datetime
import itertools
from analytics_algorithms.Recommendation import Recommendation

#TODO : for all users and posts check for their existence and also handle errors
class AdminPageData:
    """
    class to update admin data and also recommendations for users as a batch process
    """
    def __init__(self):
        self.db = current_app.db
        self.admin_db = self.db.AdminPageData
        self.users_db = self.db.Users
        self.posts_db = self.db.Posts

    def delete_post(self,post):
        postId = post["postID"]
        users_rated = post["usersRated"]
        for userId in users_rated:
            user = self.users_db.find_one({"userID": userId})
            rated_posts = user["ratedPosts"]
            # there is a faster way for update but doesn't works for free aws mongo
            self.users_db.update_one({"postID": postId}, {"$set": {"ratedPosts": rated_posts}})

        self.posts_db.remove({"postID": postId})

    def delete_posts(self):
        """
        fucntion to delete users who are marked for deletion from the database
        It deletes user and all post made by the user
        """
        posts_to_delete = self.posts_db.find({"status":"delete"})
        for post in posts_to_delete:
            self._delete_post(post)


    def delete_users(self):
        """
        fucntion to delete posts which are marked for deletion from database
        It deletes all post related  inluding ratings given to the post by the user and post from the list of post posted by the user
        """
        users_to_delete = self.users_db.find({"status":"delete"})
        for user in users_to_delete:
            userId = user["userID"]

            #remove the user from the followers list of its following users
            following_Ids = user["following"]
            for following_user_id in following_Ids:
                following_user = self.users_db.find_one({"userID":following_user_id})
                follower_list = following_user["followers"]
                #check
                follower_list.remove(userId)
                self.users_db.update_one({"userID": following_user_id}, {"$set": {"followers": follower_list}})

            #remove the user from the following list of users it follows
            followers_Ids = user["followers"]
            for follower_user_id in followers_Ids:
                follower_user = self.users_db.find_one({"userID":follower_user_id})
                following_list = follower_user["following"]
                #check
                following_list.remove(userId)
                self.users_db.update_one({"userID": follower_user_id}, {"$set": {"following": following_list}})

            #remove all my posts
            users_posts_ids = user["postIDs"]
            for user_post_id in users_posts_ids:
                post = self.posts_db.find_one({"postID": user_post_id})
                self._delete_post(post)

            #reduce ratings of all posts I rated
            posts_rated = user["ratedPosts"]
            for postId,rating in posts_rated.items():
                post = self.posts_db.find_one({"postID": postId})
                users_rated = post["usersRated"]
                users_rated.remove(userId)
                cumulative_rating = post["cumulativeRating"] - rating
                self.posts_db.update_one({"postID": postId}, {"$set": {"cumulativeRating": cumulative_rating,"usersRated":users_rated}})
            #finally delete the users data
            self.posts_db.remove({"userID": userId})





    def update_users_count_data(self):
        """
        update total user count and number of users trend
        """
        users = self.users_db.find()
        total_current_users = users.count()
        #insert present data# sort the dict and remove the last one
        admin_data = self.admin_db.find_one({"entitled":"all"})
        user_trend_count = admin_data["userCountTrend"]
        curr_date = datetime.datetime.now().strftime("%Y-%m-%d")
        del user_trend_count[min(user_trend_count.keys())]
        user_trend_count[str(curr_date)] = total_current_users
        self.admin_db.update_one({"entitled": "all"}, {"$set": {"userCountTrend":user_trend_count}})

    def get_post_value(self,post):
        """
        Function to calculate value of a post
        Currently used formula = (cummulative rating)/2 * (number of users rated)/2
        """
        cummulative_rating = post["cumulativeRating"]
        number_of_users_rated = len(post["usersRated"])
        return ((cummulative_rating/2)*(number_of_users_rated/2))

    def update_top_rated_posts(self):
        """
        updates the top rated posts data
        top rated post are decided by cummulative ratings and number of users following
        #top rated post is cummulative*numberofusers/4 . select top 50
        """
        posts = self.posts_db.find()
        posts_rating_dict = {}
        for post in posts:
            postId = post["postID"]
            posts_rating_dict[postId] = self.get_post_value(post)

        posts_rating_dict = {key: value for key, value in sorted(posts_rating_dict.items(), key=lambda item: item[1] , reverse= True)}
        #currently picks only top 10 posts

        pos_top_10 = dict(itertools.islice(posts_rating_dict.items(), 10))
        return pos_top_10


    def get_user_value(self,user):
        number_of_post = len(user["postIDs"])
        rated_posts = len(user["ratedPosts"])
        return 10*number_of_post + 0.5*rated_posts


    def update_most_active_users(self):
        """
        update most active users in the applications
        The activeness of user is decided by the number of post it posted , number of post rated , number of followers.
        #from post data get user id weight 10 and rated users 1 for per ratings
        """
        users = self.users_db.find()
        users_rating_dict = {}
        for user in users:
            userId = user["userID"]
            users_rating_dict[userId] = self.get_user_value(user)

        users_rating_dict = {key: value for key, value in
                             sorted(users_rating_dict.items(), key=lambda item: item[1], reverse=True)}
        # currently picks only top 10 posts

        user_top_10 = dict(itertools.islice(users_rating_dict.items(), max(10,len(users_rating_dict))))
        return user_top_10


    def update_users_recommendation(self):
        """
        update the recommendated post seen by user based ratings given by all users, followers of the user and the following list of user
        The post of users followed by the given user is given max of predicted rating or 4
        c
        """
        predict_rating = Recommendation.recommender_system()
        users = self.users_db.find()
        for user in users:
            userId = user["userID"]
            post_rating = predict_rating[userId]
            following = user["following"]
            for following_user_id in following:
                following_user = self.users_db.find_one({"userID":following_user_id})
                for following_user_post_id in following_user["postIds"]:
                    post_rating[following_user_post_id] = max(4,post_rating[following_user_post_id])

            post_rating = {key: value for key, value in
                                 sorted(post_rating.items(), key=lambda item: item[1], reverse=True)}

            top_100_recommendations = dict(itertools.islice(post_rating.items(), max(100,len(post_rating)))).keys()

            self.users_db.update_one({"userID": userId}, {"$set": {"ecommendedPosts":top_100_recommendations}})



