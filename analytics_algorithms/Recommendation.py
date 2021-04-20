from flask import current_app
import numpy as np
from collections import defaultdict

class Recommendation:
    """
    Class to predict users rating given to a post
    Algorithm Used : matix factorization with user and item bias
    source : https://datajobs.com/data-science-repo/Recommender-Systems-[Netflix].pdf
    """
    def __init__(self):
        self.db = current_app.db
        self.users_db = self.db.Users
        self.posts_db = self.db.Posts
        self.train_data_dict = {}
        self.user_latent_vector = {}
        self.item_latent_vecor = {}
        self.latent_dimension = 10
        self.avg_bias = 0
        self.user_bias = defaultdict(lambda: 0)
        self.item_bias = defaultdict(lambda: 0)

    def _initialise_model(self):
        """
        Function to initialise latent feature matrices , bias values and train data
        """
        postsIds = self.users_db.distinct("userID")
        userIds = self.posts_db.distinct("postID")
        self.latent_dimension = max(10,(min(len(postsIds),len(userIds)))/20)
        users = self.users_db.find()
        item_bias = defaultdict(lambda: 0) # a tuple with first value as total rating and second as number of users rated
        for user in users:
            user_rated_posts_dict = user["ratedPosts"]
            userId = user["userID"]
            self.user_latent_matrix[userId] = np.random.uniform(-1 / np.sqrt(self.latent_dimension), 1 / np.sqrt(self.latent_dimension),(1, self.latent_dimension))

            self.train_data_dict[userId] = user_rated_posts_dict
            self.user_bias[userId] = sum(user_rated_posts_dict.value())/len(user_rated_posts_dict)
            for postId,rating in user_rated_posts_dict.items():
                item_bias["postId"][0] = rating
                item_bias["postId"][1] += 1
        for postId in postsIds:
            self.item_latent_matrix[postId] =  np.random.uniform(-1 / np.sqrt(self.latent_dimension), 1 / np.sqrt(self.latent_dimension),(1, self.latent_dimension))
            if(item_bias[postId][1]):
                self.item_bias[postId] = item_bias[postId][0] / item_bias[postId][1]



    def stochastic_gradient_descent(self,l_rate:float = 0.0001 , r_rate:float = 0.1, max_iter:int = 100):
        for _ in range(max_iter):
            for userId,ratedPosts in self.train_data_dict.items():
                for postId,rating in ratedPosts.items():
                    predicted_rating = self.avg_bias + self.user_bias[userId] + self.item_bias[postId] + np.dot(self.user_latent_vector[userId],self.item_latent_vecor[postId].T)

                    error = rating - predicted_rating
                    self.user_latent_vector[userId] = self.user_latent_vector[userId] + l_rate(error*self.user_latent_vector[userId] - 2*r_rate*self.user_latent_vector[userId])
                    self.item_latent_vecor[postId] = self.item_latent_vecor[postId] + l_rate(error*self.item_latent_vecor[postId] - 2*r_rate*self.item_latent_vecor[postId])







    def recommender_system(self):
        self._initialise_model()
        self.stochastic_gradient_descent()
        result_dict = {}
        postsIds = self.users_db.distinct("userID")
        userIds = self.posts_db.distinct("postID")
        for userId in userIds:
            result_dict[userId] = {}
            for postId in postsIds:
                if(postId in self.train_data_dict[userId].keys()):
                    result_dict[userId][postId] = self.train_data_dict[userId][postId]
                else:
                    result_dict[userId][postId] = self.avg_bias + self.user_bias[userId] + self.item_bias[postId] + np.dot(self.user_latent_vector[userId],self.item_latent_vecor[postId].T)

        return result_dict