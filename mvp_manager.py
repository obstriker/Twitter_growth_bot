from mvp_browser_wrapper import *
from config import *
import config
import datetime

def get_users_followed_by_bot(reg_user, from_days_ago = FOLLOWER_LIFESPAN, limit = MAX_FOLLOWED_BY_BOT):
    followees = []
    two_weeks_ago = datetime.datetime.now() - datetime.timedelta(days = from_days_ago)
    month_ago = datetime.datetime.now() - datetime.timedelta(days = 21)
    
    followed_by_bot = list(action.select().join(action_arg)\
        .where(action.action == "follow")\
        .where(action.registered_user == reg_user)\
        .where(action.created > month_ago and action.created < two_weeks_ago)
        .limit(limit))
    
    for followee in followed_by_bot:
        try:
            followee_username = list(followee.action_args)[0].followee
            followees.append(followee_username)
        except:
            continue
        
    return followees

def reduce_followings(t, limit = MAX_UNFOLLOW_PER_DAY):
    if not t.logged_in:
        return -1
    unfollowees = get_users_followed_by_bot(t.registered_user, from_days_ago = -1, limit = limit)
    t.unfollow_batch(unfollowees)


def follow_unfollow_technique(username, password, hashtag, limit = MAX_FOLLOWING_PER_DAY):
    global t
    t = twitter_browser_wrapper()
    if not t.manual_login(username, password):
        return -1
    
    followees = t.get_users_from_hashtag_undetected(hashtag, limit = MAX_USERS_FROM_HASHTAG)
    print("Found {0} people to follow their followers!".format(followees))
    
    for followee in followees:
        if limit <= 0:
            break
        limit -= t.follow_his_followers(followee, limit = MAX_FOLLOWING_PER_DAY/4)
        random_sleep(2)
    # TODO: Unfollow expired accounts
    unfollowees = get_users_followed_by_bot(t.registered_user, limit = MAX_UNFOLLOW_PER_DAY)
    t.unfollow_batch(unfollowees)
    
    
        
    
