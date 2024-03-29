# This module performs the classic twitter growth technique of following and unfollowing.
# in the future I wil develop tweet engagement + advanced techniques.
# This should manage and work on a list of usernames (maybe get a list of usernames and execute 3 times a day).
import argparse
import sys
from config import *
from registered_user_manager import registered_user_manager
 
parser = argparse.ArgumentParser("twitter_growth_bot.py")
parser.add_argument("--username", help="The username that you want to promote", type=str)
parser.add_argument("--password", help="The password that you want to promote", type=str)
parser.add_argument("--follow-list", help="Follow this list as follow/unfollow technique", type=str)
parser.add_argument("--follow-unfollow", help="use the follow/unfollow technique", type=str)
parser.add_argument("--hashtag", help="Hashtag for interest discovery", type=str)
parser.add_argument("--reduce", help="Reduce followers who don't follow back - \
    used for debug or specific actions purpose", type=bool)
args = parser.parse_args()
    

def follow_unfollow_technique(username, password, hashtags, \
     following_per_day_limit = MAX_FOLLOWING_PER_DAY,
     unfollow_per_day_limit = MAX_UNFOLLOW_PER_DAY,
     max_follow_overall = MAX_OVERALL_FOLLOW):

    r = registered_user_manager(username, password)
    # Check if this hashtag already loaded, then decide wether to load it again.
    interesting_followers = r.load_followers_from_hashtag(hashtags)
    r.follow(interesting_followers)
    r.unfollow_followed_people()


def reduce_followers(username, password,
     unfollow_per_day_limit = MAX_UNFOLLOW_PER_DAY,
     max_unfollow_overall = MAX_OVERALL_FOLLOW):
    r = registered_user_manager(username, password)
    r.reduce_followings_who_dont_follow_back(limit = 10) 
    

def main():
    if args.follow_list:
        pass
    
    if args.hashtag:
        follow_unfollow_technique(args.username, args.password, args.hashtag)
    elif args.reduce:
        reduce_followers(args.username, args.password, args.hashtag)


if __name__ == "__main__":
    main()
