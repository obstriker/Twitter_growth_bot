from peewee import *
import datetime

import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

db = SqliteDatabase('twitter.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = TextField(unique=True)

class registered_user(BaseModel):
    user = ForeignKeyField(User, backref='registered_users', unique = True)
    username = TextField()
    password = TextField(default="")
    #desired_followers = NumericField()

class action(BaseModel):
    created = DateTimeField(default=datetime.datetime.now)
    action = TextField()
    registered_user = ForeignKeyField(registered_user, backref='actions')
    
class Follower(BaseModel):
    created = DateTimeField(default=datetime.datetime.now)
    follower = ForeignKeyField(User, backref='followers')
    followed = ForeignKeyField(User, backref='followers')
    domain = TextField(default="")
    modified = DateTimeField

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        indexes = (
        (('follower', 'followed'), True),
    )

class Tweet(BaseModel):
    user = ForeignKeyField(User, backref='tweets')
    description = TextField()
    time = TextField(default="") #DateTimeField()
    
    class Meta:
        indexes = (
        (('user', 'description'), True),
    )

class Hastag(BaseModel):
    name = TextField(unique=True)
    domain = TextField()
    
class scrape_class(BaseModel):
    created = DateTimeField(default=datetime.datetime.now)
    component_name = TextField(default = "")
    class_name = TextField(default = "")
    
    
class action_arg(BaseModel):
    action = ForeignKeyField(action, backref='action_args')
    name = TextField(default = "")
    followee = TextField(default = "", null = True) #ForeignKeyField(Follower, backref='action_args', default=None, null = True)
    #scrape_class = ForeignKeyField(scrape_class, backref='action_args', default=None)
    tweet = ForeignKeyField(Tweet, backref='action_args', default=None, null=True)


def insert_user(username):
    user = User.create(username=username)
    user.save()

def insert_users(usernames):
    for username in username:
        insert_user(username)

def create_tables():
    db.create_tables([User, Tweet, Follower, registered_user, User, action, action_arg, scrape_class], safe=True)
    
def log_action(action_type, registered_user, arg = None):
    try:
        act = action.create(action = action_type, registered_user = registered_user)
        
        if action_type == "follow" or action_type == "unfollow":
            act_arg = action_arg.create(action = act, followee = arg)
        elif action_type == "scrape_class":
            act_arg = action_arg.create(action = act, scraped_class = arg)
        elif action_type == "tweet":
            act_arg = action_arg.create(action = act, tweet = arg)
            
        act.save()
        if act_arg:
            act_arg.save()
        return True
    
    except:
        return False

def username_unfollowed_before(ruser, unfollowee):
    unfollowed_by_bot = list(action.select().join(action_arg).where(action.action == "unfollow")\
        .where(action.registered_user == ruser)
        .where(action_arg.followee == unfollowee))
    
    return len(unfollowed_by_bot) > 0        

def username_followed_before(ruser, followee):
    followed_by_bot = list(action.select().join(action_arg).where(action.action == "follow")\
        .where(action.registered_user == ruser)
        .where(action_arg.followee == followee))
    
    return len(followed_by_bot) > 0    
    
def get_users_unfollowed_by_bot(self, limit):
    followees = []
    unfollowed_by_bot = action.select().where(action.action == "unfollow")\
        .where(action.registered_user == self.registered_user)\
            .limit(min(limit, 10))
    
    for followee in unfollowed_by_bot:
        try:
            followee_username = list(followee.action_args)[0].followee
            followees.append(followee_username)
        except:
            continue
        
    return followees
      
    
def main():
    create_tables()

if __name__ == '__main__':
    main()