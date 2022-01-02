# This module performs the classic twitter growth technique of following and unfollowing.
# in the future I wil develop tweet engagement + advanced techniques.
# This should manage and work on a list of usernames (maybe get a list of usernames and execute 3 times a day).
import argparse
import sys
from twitter_interest_discovery import *

MAX_FOLLOWING_PER_DAY = 70
MAX_UNFOLLOW_PER_DAY = 40
MAX_OVERALL_FOLLOW = 1000

parser = argparse.ArgumentParser("twitter_growth_bot.py")
parser.add_argument("username", help="The username that you want to promote", type=str)
parser.add_argument("password", help="The password that you want to promote", type=str)
parser.add_argument("--follow-list", help="Follow this list as follow/unfollow technique", type=str)
parser.add_argument("--follow-unfollow", help="use the follow/unfollow technique", type=str)
parser.add_argument("--domain-hashtag", help="Hashtag for interest discovery", type=str)
args = parser.parse_args()


def follow_unfollow_technique(username, password, hashtags, \
     following_per_day_limit = MAX_FOLLOWING_PER_DAY,
     unfollow_per_day_limit = MAX_UNFOLLOW_PER_DAY,
     max_follow_overall = MAX_OVERALL_FOLLOW):

    domain_users = []
    t = twitter_browser_wrapper()

    t.login(args["username"], args["password"])
    if not t.logged_in():
        return False
    
    domain_users = get_users_from_hashtags(hashtags, limit=100)
    # insert to DB
    my_followings = t.get_username_following(args["username"])
    # insert to DB
    users_left = min(MAX_FOLLOWING_PER_DAY, MAX_OVERALL_FOLLOW - len(my_followings))

    for user in domain_users:
        if user not in my_followings and \
            users_left > 0:
            t.follow(user)
            users_left = users_left -1

    
    
    



def main():
    if 'follow-list' in args.keys():
        pass

    if 'follow-unfollow' in args.keys():
        if 'hashtag' in args.keys():
            follow_unfollow_technique(args["username"], args["password"],hashtags)


if __name__ == "__main__":
    main()
