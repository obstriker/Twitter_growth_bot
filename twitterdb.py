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

class Registered_user(BaseModel):
    username = TextField(unique=True)
    password = TextField()
    user_id = ForeignKeyField(User, backref='registered_users')



class Follower(BaseModel):
    followed_user = ForeignKeyField(User, backref='followers')
    following_user = ForeignKeyField(User, backref='followers')
    domain = ForeignKeyField(Domain_of_interest, backref='followers')
    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        indexes = (
        (('followed_user', 'following_user'), True),
    )

class Tweet(BaseModel):
    user = ForeignKeyField(User, backref='tweets')
    description = TextField()
    time = DateTimeField()

class Domain_of_interest(BaseModel):
    name = TextField(unique=True)

class Hastag(BaseModel):
    name = TextField(unique=True)
    domain = ForeignKeyField(Domain_of_interest, backref='hashtags')

def populate_test_data():
    db.create_tables([User, Tweet, Follower, Registered_user, User])

    data = (
        ('huey', ('meow', 'hiss', 'purr')),
        ('mickey', ('woof', 'whine')),
        ('zaizee', ()))
    for username, tweets in data:
        user = User.create(username=username)
        for tweet in tweets:
            Tweet.create(user=user, description=tweet, time=datetime.now())

    # Populate a few favorites for our users, such that:
    print(data)

def insert_user(username):
    user = User.create(username=username)
    user.save()

def insert_users(usernames):
    for username in username:
        insert_user(username)

def insert_follower(follower, follower, followee):
    followee = 
    follower = Follower.create(followed_user=user, following_user = user2)

db.create_tables([User, Tweet, Follower, Registered_user, User])