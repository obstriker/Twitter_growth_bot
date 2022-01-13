#Make sure I add limits to the follow/ unfollow actions.
# limit to max actions per day, overall goal.
#TODO: do the domain interest harvest one time and achieve X followers.
# Then keep using it as long as needed. -> first time will take time but the next daily runs will be fast
#TODO: update the script to recognize people that I followed and then unfollowed (don't follow them again)
#TODO: add delay between each follow
#TODO: Add pause button to let the user edit the page, lists in live.
import datetime
from config import *
from twitter_browser_wrapper import twitter_browser_wrapper
from twitterdb import *
from twitter_interest_discovery import twitter_interest_discovery

class registered_user_manager:
    domain_followees = []
    
    def __init__(self, username, password):
        #insert user details to db if it's not exists already
        #add overall max followers for every individual user
        
        self.t = twitter_browser_wrapper()
        self.t.login(username, password)
        
        self.followings = self.t.get_username_followings(username)
        self.followers = self.t.get_username_followers(username)
        
        user = User.get_or_create(username = username)[0]
        self.registered_user = registered_user.get_or_create(\
            user = user, username = username, password = password)[0]
        
        self.following_left = MAX_FOLLOWING_PER_DAY - \
            len(list(action.select().where(action.registered_user == self.registered_user\
            and action.action == "follow"\
            and action.created > datetime.datetime.now() - datetime.timedelta(days=1))))
        
        self.unfollowing_left = MAX_UNFOLLOW_PER_DAY - \
            len(list(action.select().where(action.registered_user == self.registered_user\
            and action.action == "unfollow"\
            and action.created > datetime.datetime.now() - datetime.timedelta(days=1))))
    
    def unfollow_followed_people(self, \
        limit = MAX_UNFOLLOW_PER_DAY):
        # unfollow people that the bot has followed if their time is up
        # unfollow the people who does not follow back first (which are expired)
        followed_by_bot = action.select().where(action.action == "follow")\
            .where(action.registered_user == self.registered_user)\
                .limit(min(limit, 10))
        
        for act_on_followee in followed_by_bot:
            if datetime.datetime.now() - datetime.timedelta(days=FOLLOWER_LIFESPAN) < act_on_followee.created:
                if action_arg.get(action_arg.action == act_on_followee).follow \
                     in self.followings and self.unfollowing_left > 0:
                        self.t.unfollow(act_arg.follow.followed.username)
                        self.unfollowing_left = self.unfollowing_left - 1
    
    def load_followers_from_hashtag(self, hashtag):
        # Get a list of followers that im interested in
        #that I don't follow.
        #TODO: add support for incremental followers(every load will be added to domain_followees)
        
         self.domain_followees = \
             twitter_interest_discovery.get_followers_from_hashtag(\
                 self.t,hashtag, limit =\
                     min(MAX_OVERALL_FOLLOW, MAX_FOLLOWING_PER_DAY))
        
         return self.domain_followees
    
    def follow(self, followees):
        for followee in followees:
            if self.following_left > 0:
                self.t.follow(followee.replace("@",""))
                self.following_left = self.following_left - 1
                
#r = registered_user_manager(TEST_USERNAME, TEST_PASSWORD)
#interesting_fols = r.load_followers_from_hashtag()
#r.follow(tid)
#r.unfollow_followed_people()