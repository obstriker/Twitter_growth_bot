# This module performs the classic twitter growth technique of following and unfollowing.
# in the future I wil develop tweet engagement + advanced techniques.
# This should manage and work on a list of usernames (maybe get a list of usernames and execute 3 times a day).
import argparse
import sys
from config import *
import mvp_manager

parser = argparse.ArgumentParser("twitter_growth_bot.py")
parser.add_argument("-u","--username", help="The username that you want to promote", type=str)
parser.add_argument("-p","--password", help="The password that you want to promote", type=str)
parser.add_argument("--follow-list", help="Follow this list as follow/unfollow technique", type=str)
parser.add_argument("-fu","--follow-unfollow", help="use the follow/unfollow technique", type=str)
parser.add_argument("--hashtag", help="Hashtag for interest discovery", type=str)
parser.add_argument("-f","-filename", help="Select filename that contains multiple accounts", type=str)
parser.add_argument("-r","--reduce", help="Reduce followers who don't follow back - \
    used for debug or specific actions purpose", action='store_true')
parser.add_argument("--mvp", help="enable mvp testing", action='store_true')
parser.add_argument("--followees", help="target specific influencers", type=str)
args = parser.parse_args()

def reduce_followers(username, password,
     unfollow_per_day_limit = MAX_UNFOLLOW_PER_DAY,
     max_unfollow_overall = MAX_OVERALL_FOLLOW):
    #r = registered_user_manager(username, password)
    #r.reduce_followings_who_dont_follow_back(limit = 10)
    mvp_manager.reduce_followings(mvp_manager.t, limit = 5)
    
def mvp_follow_technique(username, password, hashtag, \
     following_per_day_limit = MAX_FOLLOWING_PER_DAY,
     unfollow_per_day_limit = MAX_UNFOLLOW_PER_DAY,
     max_follow_overall = MAX_OVERALL_FOLLOW,
     followees = []):
    mvp_manager.follow_unfollow_technique(username, password, hashtag, followees)
    #mvp_manager.reduce_followings(mvp_manager.t, limit = 5)
    
def loop_accounts(filename):
    with open(filename, 'r') as f:
        for line in f:
            if not line:
                contine
                
            line = line.replace("\n","").split(":")
            if len(line) == 3:
                mvp_follow_technique(line[0], line[1], line[2])
    
def main():
    if args.follow_list:
        pass
    
    followees = []
    if args.followees: 
        followees = args.followees.replace(" ", "").split(",")
    
    if args.f:
        loop_accounts(args.f)
    elif args.mvp and args.hashtag:
        mvp_follow_technique(args.username, args.password, args.hashtag, followees = followees)
    elif args.reduce:
        reduce_followers(args.username, args.password, args.hashtag)


if __name__ == "__main__":
    main()
