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

# create logger with 'spam_application'
logger = logging.getLogger('browser_wrapper')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('twitter.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

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
            len(list(action.select().where(action.registered_user == self.registered_user)\
            .where(action.action == "follow")\
            .where(action.created > datetime.datetime.now() - datetime.timedelta(days=1))))
        
        self.unfollowing_left = MAX_UNFOLLOW_PER_DAY - \
            len(list(action.select().where(action.registered_user == self.registered_user)\
            .where(action.action == "unfollow")\
            .where(action.created > datetime.datetime.now() - datetime.timedelta(days=1))))
    
    def _get_users_followed_by_bot(self, limit):
        followees = []
        two_weeks_ago = datetime.datetime.now() - datetime.timedelta(days = FOLLOWER_LIFESPAN)
        month_ago = datetime.datetime.now() - datetime.timedelta(days = 21)
        
        followed_by_bot = list(action.select()\
            .where(action.action == "follow")\
            .where(action.registered_user == self.registered_user)\
                .where(action.created > month_ago and action.created < two_weeks_ago)\
                .limit(min(limit, 10)))
        
        for followee in followed_by_bot:
            try:
                followee_username = list(followee.action_args)[0].followee
                followees.append(followee_username)
            except:
                continue
            
        return followees
    
    def _get_users_unfollowed_by_bot(self, limit):
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
    
    def _is_followee_unfollowed_by_bot(self, followee):
        unfollowed = list(action.select().join(action_arg).where(action.action == "unfollow")\
            .where(action.registered_user == self.registered_user)
            .where(action_arg.followee ==  followee))

        return len(unfollowed) > 0
    def _is_followee_follows_back(self, followee):
        pass
    
    # IN: username -> actions:
    # 1. Reduce followings that do not follow me back.
    # 2. Remove expired followings (for bot only)
    # 3. 
    def unfollow_followed_people(self, \
        keep_mutual_followers = False, \
        limit = MAX_UNFOLLOW_PER_DAY):
        # unfollow people that the bot has followed if their time is up
        # unfollow the people who does not follow back first (which are expired)
        # If I unfollowed you before then I won't follow you again
        followed_by_bot = self._get_users_unfollowed_by_bot(limit)
        
        unfollowed_by_bot = self._get_users_unfollowed_by_bot(limit)
                
        for act_on_followee in followed_by_bot:
            for act_arg in act_on_followee.action_args:
                if act_arg.followee in already_unfollowed_users:
                    continue
            
            act_follower = Follower.get(Follower.follower == User.get_or_create(username = self.registered_user.username)[0] and\
                Follower.followed == User.get(User.username == followee_username))
            
            if act_follower in self.followings\
                and followee_username not in already_unfollowed_users\
                    and self.unfollowing_left > 0:
                if keep_mutual_followers and act_follower in self.followers:
                    continue
                self.t.unfollow(act_arg.followee)
                self.unfollowing_left -= 1
                    
    def reduce_followings_who_dont_follow_back(self, limit = MAX_UNFOLLOW_PER_DAY):
        for followee in self.followings:
            if followee in self.followers:
                continue
            
            if self.following_left > 0 \
                and limit > 0:
                    self.t.unfollow(followee)
                    self.following_left -= 1
                    limit -= 1
                        
                    
                
    
    def load_followers_from_hashtag(self, hashtag, limit = MAX_FOLLOWING_PER_DAY):
        # Get a list of followers that im interested in
        #that I don't follow.
        #TODO: add support for incremental followers(every load will be added to domain_followees)
        
         self.domain_followees = \
             twitter_interest_discovery.get_followers_from_hashtag(\
                 self.t,hashtag, limit =\
                     min(MAX_OVERALL_FOLLOW, MAX_FOLLOWING_PER_DAY))
        
         return self.domain_followees
    
    def follow(self, followees):
        follow_left_before = self.following_left
        for followee in followees:
            if self.following_left <= 0:
                break
            
            self.t.follow(followee.replace("@",""))
            self.following_left -= 1
            logger.info("Username:{0} followed {1}".format(self.registered_user.username, followee.replace("@","")))
        
        return follow_left_before - self.following_left
                
                
#r = registered_user_manager(TEST_USERNAME, TEST_PASSWORD)
#interesting_fols = r.load_followers_from_hashtag()
#r.follow(tid)
#r.unfollow_followed_people()