from mvp_browser_wrapper import *
from config import *
import config

def get_users_followed_by_bot(reg_user, from_days_ago = FOLLOWER_LIFESPAN, limit = 40):
    followees = []
    two_weeks_ago = datetime.datetime.now() - datetime.timedelta(days = from_days_ago)
    month_ago = datetime.datetime.now() - datetime.timedelta(days = 21)
    
    followed_by_bot = list(action.select().join(action_arg)\
        .where(action.action == "follow")\
        .where(action.registered_user == reg_user)\
        .where(action.created > month_ago and action.created < two_weeks_ago))
    
    for followee in followed_by_bot:
        try:
            followee_username = list(followee.action_args)[0].followee
            followees.append(followee_username)
        except:
            continue
        
    return followees

def reduce_followings(t, limit = REDUCE_FOLLOWERS_LIMIT):
    unfollowees = get_users_followed_by_bot(t.registered_user, from_days_ago = -1)
    t.unfollow_batch(unfollowees)


def follow_unfollow_technique(username, password, hashtag):
    global t
    t = twitter_browser_wrapper()
    t.login(username, password)
    followees = t.get_users_from_hashtag_undetected(hashtag, limit = 1)
    
    
    for followee in followees:
        t.follow_his_followers(followee, limit = 4)
        
    # TODO: Unfollow expired accounts
    unfollowees = get_users_followed_by_bot(t.registered_user)
    t.unfollow_batch(unfollowees)
    
    
        
    
