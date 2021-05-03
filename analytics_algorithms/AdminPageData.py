from flask import current_app
import datetime
import itertools
from analytics_algorithms.Recommendation import Recommendation
from collections import defaultdict
import numpy as np

class AdminPageData:
    """
    class to update admin data and also recommendations for users as a batch process
    """
    def __init__(self):
        self.db = current_app.db
        self.admin_db = current_app.db.AdminPageData
        self.users_db = current_app.db.Users
        self.posts_db = current_app.db.Posts
        self.reported_posts_db = current_app.db.ReportedPosts

    def _delete_post(self,post):
        if(not post):
            return
        postId = post["postID"]
        userId = post["userID"]
        current_app.logger.info("deleting post : %s ", postId)
        user_posted = self.users_db.find_one({"userID": userId})
        postIds = user_posted["postIDs"]
        postIds.remove(postId)
        self.users_db.update_one({"userID": userId}, {"$set": {"postIDs": postIds}})
        users_rated = post["ratedBy"]

        for userId in users_rated:
            user = self.users_db.find_one({"userID": userId})
            rated_posts = np.asarray(user["ratedPosts"])
            post_ids = rated_posts[:,0].tolist()
            index = post_ids.index(postId)
            rated_posts = rated_posts.tolist()
            del rated_posts[index]
            # there is a faster way for update but doesn't works for free aws mongo
            self.users_db.update_one({"userID": userId}, {"$set": {"ratedPosts": rated_posts}})
        current_app.logger.info("post deleted : %s ", postId)
        self.posts_db.remove({"postID": postId})
        self.reported_posts_db.delete_many({"postID": postId})


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
            current_app.logger.info("deleting user : %s ", userId)
            #remove the user from the followers list of its following users
            following_Ids = user["following"]
            for following_user_id in following_Ids:
                current_app.logger.info("removing %s user from follower list of user %s  ", userId ,following_user_id)
                following_user = self.users_db.find_one({"userID":following_user_id})
                if(not following_user):
                    continue
                follower_list = following_user["followers"]
                if(userId in follower_list):
                    follower_list.remove(userId)
                self.users_db.update_one({"userID": following_user_id}, {"$set": {"followers": follower_list}})

            #remove the user from the following list of users it follows
            followers_Ids = user["followers"]
            for follower_user_id in followers_Ids:
                current_app.logger.info("removing %s user from following list of user %s ", userId,
                                        follower_user_id)
                follower_user = self.users_db.find_one({"userID":follower_user_id})
                if(not follower_user):
                    continue
                following_list = follower_user["following"]
                if (userId in following_list):
                    following_list.remove(userId)
                self.users_db.update_one({"userID": follower_user_id}, {"$set": {"following": following_list}})

            #remove all my posts
            users_posts_ids = user["postIDs"]
            for user_post_id in users_posts_ids:
                current_app.logger.info("removing %s post  of user %s  ", user_post_id,userId)
                post = self.posts_db.find_one({"postID": user_post_id})
                self._delete_post(post)

            #reduce ratings of all posts User rated
            posts_rated = user["ratedPosts"]
            for postId,rating in posts_rated:
                current_app.logger.info("changing %s post  rated by user %s  ", postId, userId)
                post = self.posts_db.find_one({"postID": postId})
                if(not post ):
                    continue
                users_rated = post["ratedBy"]
                cumulative_rating = post["cumulativeRating"]
                if(userId in users_rated):
                    users_rated.remove(userId)
                    cumulative_rating -= int(rating)
                self.posts_db.update_one({"postID": postId}, {"$set": {"cumulativeRating": cumulative_rating,"ratedBy":users_rated}})
            #finally delete the users data
            self.users_db.remove({"userID": userId})
            current_app.logger.info("deleted user : %s ", userId)
            self.reported_posts_db.delete_many({"postUserID": userId})





    def update_users_count_data(self):
        """
        update total user count and number of users trend
        """
        current_app.logger.info("Updating users trend  ")
        users = self.users_db.find({"status":"active"})
        total_current_users = users.count()
        #insert present data# sort the dict and remove the last one
        admin_data = self.admin_db.find_one({"entitled":"all"})
        user_trend_count = admin_data["userCountTrend"]
        curr_date = datetime.datetime.now().strftime("%Y-%m-%d")
        min_key = min(user_trend_count.keys())
        if(len(user_trend_count)>=10):
            keys = list(user_trend_count.keys())
            sorted(keys, key=lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))
            del user_trend_count[keys[0]]
        user_trend_count[str(curr_date)] = total_current_users
        self.admin_db.update_one({"entitled": "all"}, {"$set": {"userCountTrend":user_trend_count}})

    def get_post_value(self,post):
        """
        Function to calculate value of a post
        Currently used formula = (cummulative rating)/2 * (number of users rated)/2
        """
        cummulative_rating = post["cumulativeRating"]
        number_of_users_rated = len(post["ratedBy"])
        return ((cummulative_rating/2)*(number_of_users_rated/2))

    def update_top_rated_posts(self):
        """
        updates the top rated posts data
        top rated post are decided by cummulative ratings and number of users following
        #top rated post is cummulative*numberofusers/4 . select top 50
        """
        current_app.logger.info("Updating top rated posts  ")
        posts = self.posts_db.find()
        posts_rating_dict = {}
        for post in posts:
            postId = post["postID"]
            posts_rating_dict[postId] = self.get_post_value(post)

        posts_rating_dict = {key: value for key, value in sorted(posts_rating_dict.items(), key=lambda item: item[1] , reverse= True)}
        #currently picks only top 10 posts

        pos_top_10 = dict(itertools.islice(posts_rating_dict.items(), min(10,len(posts_rating_dict))))
        self.admin_db.update_one({"entitled": "all"}, {"$set": {"topRatedPost":[*pos_top_10]}})

    def update_reported_posts_and_users(self):
        """
        updates the more than 3 times reported posts data

        """
        current_app.logger.info("Updating  reported posts  ")
        reported_posts = self.reported_posts_db.find({})
        users_times_reported_dict = defaultdict(lambda: 0)
        posts_times_reported_dict = defaultdict(lambda: 0)
        for reported_post in reported_posts:
            userId = reported_post["postUserID"]
            postId = reported_post["postID"]
            users_times_reported_dict[userId] += 1
            posts_times_reported_dict[postId] += 1

        users_times_reported_dict = {key: value for key, value in
                             sorted(users_times_reported_dict.items(), key=lambda item: item[1], reverse=True)}

        posts_times_reported_dict = {key: value for key, value in
                                     sorted(posts_times_reported_dict.items(), key=lambda item: item[1], reverse=True)}

        self.admin_db.update_one({"entitled": "all"}, {"$set": {"reportedPosts": posts_times_reported_dict,"reportedUsers":users_times_reported_dict}})



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
        current_app.logger.info("Updating  most active users  ")
        users = self.users_db.find()
        users_rating_dict = {}
        for user in users:
            userId = user["userName"]
            users_rating_dict[userId] = self.get_user_value(user)

        users_rating_dict = {key: value for key, value in
                             sorted(users_rating_dict.items(), key=lambda item: item[1], reverse=True)}
        # currently picks only top 10 posts

        user_top_10 = dict(itertools.islice(users_rating_dict.items(), min(10,len(users_rating_dict))))
        self.admin_db.update_one({"entitled": "all"}, {"$set": {"mostActiveUsers":[*user_top_10]}})


    def update_users_recommendation(self):
        """
        update the recommendated post seen by user based ratings given by all users, followers of the user and the following list of user
        The post of users followed by the given user is given max of predicted rating or 4
        c
        """
        predict_rating = Recommendation().recommender_system()

        users = self.users_db.find()
        for user in users:
            userId = user["userID"]
            current_app.logger.info("Updating recommended post for user %s",userId)
            post_rating = predict_rating[userId]
            following = user["following"]
            for following_user_id in following:
                following_user = self.users_db.find_one({"userID":following_user_id})
                if(following_user):
                    for following_user_post_id in following_user["postIDs"]:
                        post_rating[following_user_post_id] = max(4,post_rating[following_user_post_id])

            post_rating = {key: value for key, value in
                                 sorted(post_rating.items(), key=lambda item: item[1], reverse=True)}

            top_10_recommendations = dict(itertools.islice(post_rating.items(), max(10,len(post_rating))))

            self.users_db.update_one({"userID": userId}, {"$set": {"recommendedPosts":[*top_10_recommendations]}})





