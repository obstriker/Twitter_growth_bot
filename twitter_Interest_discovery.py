# This module gets a username(s) and crawls through his tweets and collects hashtags.
# This module provides a few functionalities:
# 1. in: username -> out: hashtags
# 1. in: hashtag -> out: more hashtags in the same domain
# 2. in: username -> out: usernames in the same domain
# 3. in: hashtag  -> out: usernames that posted tweet with this hashtag (limited)
# 4. in: username -> out: username -> out: followers (target audience)
# 4. in: hashtag -> out: username -> out: followers (target audience)
import getpass

import twitter_api_wrapper

tweetlimit = 10
import twitter_browser_wrapper


class twitter_intrest_discovery:

    def __init__(self):
        t = twitter_browser_wrapper()
        t.login(twitter_browser_wrapper.TEST_USERNAME, twitter_browser_wrapper.TEST_PASSWORD)

    def gethashfromuser(self, user):
        hashtags = []
        t = twitter_api_wrapper.get_username_tweets(self, user)
        for x in t:
            for word in x.description.split(" "):
                if "#" in word:
                    hashtags.append(word)
        return hashtags

    def gethashfromhash(self, hash):
        hashtags = []
        t = twitter_api_wrapper.get_hashtag_tweets(self, hash)
        for x in t:
            for word in x.description.split(" "):
                if "#" in word:
                    hashtags.append(word)
        return hashtags

    def getuserfromuser(self, user):
        users = []
        hashtags = self.gethashfromuser(user)
        for hashtag in hashtags:
            users += self.getuserfromhash(hashtag)
        return users

    def getuserfromhash(self, hash):
        users = []
        t = twitter_api_wrapper.get_username_tweets(self, hash)
        for x in t:
            users.append(x.username)
        return users

    def getuserfollowfromuser(self,user):
        users = []
        t = twitter_api_wrapper.