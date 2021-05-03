# ChooseNXT Analytics App 

## About 
This is a sister project related to the ChooseNXT mobile app projected (previously known as Woolala). The analytics app is a web application using Flask framework. Its purpose is for desginated admins to view and manage the current content available in the 

## Installation 
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

## Database 
The app shares the same database with the ChooseNXT mobile app so that it can access and view the activities of the mobile app users. It uses MongoDB. Please contact the customer for login credentials.

## Blueprints - Adminn App
This blueprint contains all the interface logic for the app. It includes routes for login/logout, removing reported users and posts by marking the status to delete. In addition, it has the update route, which permanently remove selected reported users and posts. In addition, it updates the recommneded posts for users. 

## Analytics Algorithm 
Each user is assigned a rating depending on the number of posts and the number of followers. Based on this, the algorithm updates recommending posts for the user. 

## Frontend 
The current application uses [Bootstrap 4.0](https://getbootstrap.com/docs/4.0/getting-started/introduction/) for styling. The app uses Jinja for web template. 

