# ChooseNXT Analytics App 

## About 
This is a sister project related to the ChooseNXT mobile app projected (previously known as Woolala). The analytics app is a web application using Flask framework. Its purpose is for desginated admins to view and manage the current content available in the application database. It gives admin ability to do statistical analysis of the usuage of mobile application, analysis about the most active users and most popular post. It gives admin control to remove users and posts, not abiding by the policies and update the model used for recommendation of desired post to users.


## Installation in development Environment
The project requires at minimum Python3. Clone the current repository and create a virtual environment for it. Once the virtual enviroment is running, install the dependencies specified in `requirements.txt`. 
``` bash 
$ git clone git@github.com:FashioNXT/woolala-analytics-app.git
$ cd woolala-analytics-app
$ pip install -r requriements.txt
```

[Download and install Heroku cli](https://devcenter.heroku.com/articles/heroku-cli#download-and-install. ), if have not already. 
Please contact the custermer for login credentials. 

Sign in and add the repository to Heroku remote one. Verify that there are two remotes. 
```bash 
$ heroku login 
$ heroku git:remote -a woolala-analytics-app
$ git remote -v 
```

## Overall Framework
The applicatioin is build using flask framework to make it light weight. For information about flask framework : https://flask.palletsprojects.com/en/1.1.x/

The app.py is the main runnable file of the application. The configuration of the database can be changed in ConfigFile.properties. The application has been divided into bluprints to keep the logic losely coupled. The blueprints needs to be registered to th application in the app.py file.

This tool is currently deployed on heroku but uses a test collection with same schema as the production env collection. Later the collection can be switched easily by swtiching the env in ConfigFile.properties. 


## Database 
The app shares the same database with the ChooseNXT mobile app so that it can access and view the activities of the mobile app users. It uses MongoDB. Please contact the customer for login credentials. We have used Pymongo Library for database interaction . For more information about Pymongo : https://pymongo.readthedocs.io/en/stable/


## Blueprints - Adminn App
This blueprint contains all the interface logic for the app. It includes routes for login/logout, removing reported users and posts by marking the status to delete. In addition, it has the update route, which permanently remove selected reported users and posts. In addition, it updates the recommneded posts for users. 
More information about blueprints : https://flask.palletsprojects.com/en/1.1.x/blueprints/



## Analytics and Machine Learning Algorithm 
Currently we have implements logic to decide the most popular post, most active users and matrix factorization based recommendation systems.
# User Populrity Logic :
We are deciding the populrity of the user based on number of post the user is posting and the the number of post a user is rating. Each user is given a score based on the formula : 10*number_of_post + 0.5*rated_posts. We are then sorting users based on this score value to decide the most popular users. The formula is defined in get_user_value function in the AdminPageData.py. 

# Post Populrity Logic:
We are deciding the popularity of a post based on the number of users interacting with it . For now we are measuring interaction based on the total ratings and number of users who rated a post.
Each post is given a score based on the formula : (cummulative rating)/2 * (number of users rated)/2. Post are then sorted based on this score to decide the popularity of it.
The formula is defined in get_post_value function in the AdminPageData.py. 

# Recommendation System:
We have a build a recommendation system based on the Koren's neighbourhood model of recommendation for items to users which is latent feature based model 
We are maininting a matrix in which the row depicts users and columns depicts posts. The cell in matrix contains a score (currently decided by ratind given by the user to a post). The post by the users whom a particualar user is following is given a defualt rating of 4 to give more weightage to it before starting the training. The recommendation is made using the predicted rating . The code for recommendation is in analytics_algorithms/recommendation.py file. It used stochastic gradient decent to train the model.


Sources : https://datajobs.com/data-science-repo/Recommender-Systems-[Netflix].pdf


## Frontend 
The current application uses [Bootstrap 4.0](https://getbootstrap.com/docs/4.0/getting-started/introduction/) for styling. The app uses Jinja for web template. 

