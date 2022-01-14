# This module gets a username(s) and crawls through his tweets and collects hashtags.
# This module provides a few functionalities:
# 1. in: username -> out: hashtags
# 1. in: hashtag -> out: more hashtags in the same domain
# 2. in: username -> out: usernames in the same domain
# 3. in: hashtag  -> out: usernames that posted tweet with this hashtag (limited)
# 4. in: username -> out: username -> out: followers (target audience)
# 4. in: hashtag -> out: username -> out: followers (target audience)
from twitter_browser_wrapper import *
from twitterdb import *

TWEET_LIMIT = 10

class twitter_interest_discovery:
    def get_hashtags_from_user(t, user):
        hashtags = []
        for x in t.get_username_tweets(user):
            for word in x.description.split(" "):
                if "#" in word:
                    hashtags.append(word)
        return hashtags

    def get_hashtags_from_hashtag(t, hashtag):
        hashtags = []
        for hashtag in t.get_hashtag_tweets(hashtag):
            for word in hashtag.description.split(" "):
                if "#" in word:
                    hashtags.append(word)
        return list(set(hashtags))

    def get_users_from_user(t, user):
        users = []
        hashtags = twitter_interest_discovery.get_hashtags_from_user(t, user)
        for hashtag in hashtags:
            users += twitter_interest_discovery.get_users_from_hashtag(t, hashtag)
        return list(set(users))

    def get_users_from_hashtag(t, hashtag):
        users = []
        for tweet in t.get_hashtag_tweets(hashtag):
            users.append(tweet.username)
        return list(set(users))

    def get_users_from_hashtags(t, hashtags, limit = 100):
        users = []

        for hashtag in hashtags:
            users.append(get_users_from_hashtag(hashtag))

        return users

    def get_followers_from_hashtag(t, hashtag):
        followers = []
        users = twitter_interest_discovery.get_users_from_hashtag(t, hashtag)
        for user in users:
            followers = twitter_browser_wrapper.get_username_followers(user)
            for follower in followers:
                followers.append(follower.username)
        return list(set(followers))