# This module handles the selenium browser and navigates to do simple jobs at the twitter page.
# This module goal is to follow/unfollow people with minimal activities and not getting caught.

# Bot supports maximum followings/unfollowings
# Bot will follow/unfollow through followers/following page
# Bot will save all followed people to DB with the user we took them from
# that way we can unfollow them. Another way is crossing followed people
# from DB with 


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import os
import logging
import pickle
from time import sleep
import re
import urllib
import hashlib
from twitterdb import Tweet, User, Follower
from scrape_classes import *
from twitterdb import log_action
from config import *

opts = Options()
opts.headless = False

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

class twitter_browser_wrapper:
    driver = None
    def __init__(self):
        self.driver = webdriver.Firefox(options=opts)
        self.logged_in = False
        
    def __save_cookies(self, cookie_filename):
        pickle.dump( self.driver.get_cookies() , open(cookie_filename,"wb"))

    #Does it check if it's exist?
    def __load_cookies(self, cookie_filename):
        if(os.path.isfile(cookie_filename)):
            cookies = pickle.load(open(cookie_filename, "rb"))
        
            for cookie in cookies:
                self.driver.add_cookie(cookie)
                
            return True
        else:
            return False

    def __check_for_login_indicator(self, username):
        self.driver.get(TWITTER_HOMEPAGE_URL)

        if username in self.driver.page_source:
            return True
        else:
            return False

    def am_i_following(self, username):
        self.driver.get(TWITTER_BASE_URL + username)
        if "Following" in self.driver.page_source:
            t = Follower.get_or_create(follower = self.username, followed = username)[0]
            return True
        else:
            return False

    def login(self, username, password):
        self.driver.get(TWITTER_HOMEPAGE_URL)
        if self._twitter_browser_wrapper__load_cookies(COOKIE_FILENAME_FORMAT.format(username)) \
            and self._twitter_browser_wrapper__check_for_login_indicator(username):
            self.logged_in = True
            self.username = username
            user = User.get_or_create(username = username)[0]
            self.registered_user = registered_user.get_or_create(\
                user = user, username = username, password = password)[0]
            log_action("login", self.registered_user)
            # Log that login has been executed for user- username and save his preferences
            return True

        # Can be changed or blocked overtime
        self.driver.get(TWITTER_SIGN_IN_URL)
        elem = self.driver.find_element_by_tag_name("body")
        sleep(5)
        for i in range(0,3):
            elem.send_keys(Keys.TAB)

        elem.send_keys(username)
        sleep(0.5)
        elem.send_keys(Keys.ENTER)
        sleep(1)
        elem.send_keys(password)
        sleep(0.5)
        elem.send_keys(Keys.ENTER)
        sleep(1)

        if self._twitter_browser_wrapper__check_for_login_indicator(username):
            self._twitter_browser_wrapper__save_cookies(COOKIE_FILENAME_FORMAT.format(username))
            self.logged_in = True
            
            #log action - login successfull manually
            user = User.get_or_create(username = username)[0]
            self.username = username # redundant
            self.registered_user = registered_user.get_or_create(\
                user = user, username = username, password = password)[0]
            log_action("login", self.registered_user)
            
            return True
        else:
            self.logged_in = False
            #log action - login failed
            return False

# minimum activities
# limit feature
# scrolling
# dont follow previously followed people
# 
# Future:
# human-like behaviour (scrolling, clickling, pause times)
    def follow_his_followers(self, username, limit = 40):
        self.driver.get(USERNAME_FOLLOWERS_URL.format(username))
        follow_btn_opponents = None

        sleep(2)
        # Check if this works
        while followees_growing and limit > 0:
            followers_growing = False
            follow_btn_opponents = self.driver.find_elements_by_xpath("//div[contains(., 'Follow')]")

            for follow_btn in follow_btn_opponents:
                if "Follow @" not in follow_btn.get_attribute("aria-label"):
                    continue
                
                username = follow_btn.get_attribute("aria-label").split("@")[1]

                # if username has been followed before -> continue 
                # follow username
                # create follow record & followees_growing = True


#                followee = User.get_or_create(username = followee.replace("@",""))[0]
#                followed = User.get_or_create(username = username)[0]
#                f = Follower.get_or_create(follower = followee, followed = followed)[0]
                
#                if followee.username not in extracted_followers:
#                    extracted_followers.append(followee.username)
                    # Follow the username and add to DB
#                    followers_growing = True

            #Scroll down to find more tweets
            elem = self.driver.find_element_by_tag_name("body")
            elem.send_keys(Keys.END)
            sleep(SCROLL_PAUSE_TIME)

        follow_btn_opponents = self.driver.find_elements_by_xpath("//div[contains(., 'Follow')]")
        for follow_btn in follow_btn_opponents:
            if "Follow @" in follow_btn.get_attribute("aria-label"):
                username = follow_btn.get_attribute("aria-label").split("@")[1]
                # Check username with DB, if it's okay continue.
                follow_btn.click()
                
                followee = User.get_or_create(username = self.username)[0]
                followed = User.get_or_create(username = username)[0]
                f = Follower.get_or_create(follower = followee , followed = followed)[0]
                log_action("follow", self.registered_user, username)
                
                # Decrease limit variable

                return True

    def unfollow(self, username):
        self.driver.get(TWITTER_BASE_URL + username)
        sleep(0.4) # wait for page to load
        unfollow_btn_opponents = None

        # Check if this works
        unfollow_btn_opponents = self.driver.find_elements_by_xpath("//div[contains(., 'Following')]")
        if unfollow_btn_opponents:
            for unfollow_btn in unfollow_btn_opponents:
                if unfollow_btn.get_attribute("aria-label") == ("Following @" + username):
                    unfollow_btn.click()
                    sleep(0.5)
                    elem = self.driver.find_element_by_tag_name("body")
                    elem.send_keys(Keys.TAB)
                    sleep(0.5)
                    elem.send_keys(Keys.TAB)
                    sleep(0.5)
                    elem.send_keys(Keys.ENTER)
                    sleep(0.5)
                    
                    try:
                        f = Follower.remove(Follower.select().where(\
                        Follower.follower.contains(self.username) and \
                        Follower.followed.contains(username)))
                    except:
                        pass
                    
                    log_action("unfollow", self.registered_user, username)
                    
                    return True


    def follow_username_followers(self, username, limit = 100):
        extracted_followers = []
        followers_growing = True

        if not self.logged_in:
             return []
        
        if not hasattr(self, 'scm'):
            self.scm = scrape_class_manager(self.driver)
            
        if not self.scm.tscu.followers:
            self.scm.tscu.find_static_followers_class()

        self.driver.get(USERNAME_FOLLOWERS_URL.format(username))
        sleep(3)

        while followers_growing and len(extracted_followers) < limit:
            followers_growing = False
            followers = self.scm.tscu.find_relative_followers_class(username.replace("@",""))

            for follower in followers:
                follower = User.get_or_create(username = follower.replace("@",""))[0]
                followed = User.get_or_create(username = username)[0]
                f = Follower.get_or_create(follower = follower, followed = followed)[0]
                
                if follower.username not in extracted_followers:
                    extracted_followers.append(follower.username)
                    # Follow the username and add to DB
                    followers_growing = True

            #Scroll down to find more tweets
            elem = self.driver.find_element_by_tag_name("body")
            elem.send_keys(Keys.END)
            sleep(SCROLL_PAUSE_TIME)

        return extracted_followers

    def get_username_followings(self, username, limit = FOLLOWINGS_LIMIT):
        extracted_following = []
        following_growing = True

        if not self.logged_in:
             return []
        
        if not hasattr(self, 'scm'):
            self.scm = scrape_class_manager(self.driver)
            
        if not self.scm.tscu.following:
            self.scm.tscu.find_static_following_class()

        self.driver.get(USERNAME_FOLLOWING_URL.format(username))
        sleep(3)

        while following_growing and len(extracted_following) < limit:
            following_growing = False
            following = self.scm.tscu.find_relative_following_class(username)

            for followee in following:
                followed = User.get_or_create(username = followee.replace("@",""))[0]
                follower = User.get_or_create(username = username)[0]
                f = Follower.get_or_create(follower = follower, \
                    followed = followed)[0]
                
                if followed.username not in extracted_following:
                    extracted_following.append(followed.username)
                    following_growing = True

            #Scroll down to find more tweets
            elem = self.driver.find_element_by_tag_name("body")
            elem.send_keys(Keys.END)
            sleep(SCROLL_PAUSE_TIME)

        return extracted_following

        
    #TODO: how to load dynamic tweets? (click space and go down?)
    def search_tweets(self, term, limit=20):
        tweets = {}
        tweets_growing = True

        if self.logged_in:
            if not hasattr(self, 'scm'):
                self.scm = scrape_class_manager(self.driver)
                
            if not self.scm.tsc.block:
                self.scm.tsc.find_static_block()

            self.driver.get(TWITTER_SEARCH_URL.format(urllib.parse.quote(term)))
            sleep(3)

            while tweets_growing and len(tweets) < limit:
                tweets_growing = False
                articles = self.scm.tsc.find_relative_blocks()
                
                for article in articles:
                    #Create tweet object
                    tw = self.scm.tsc.article_to_tweet(article)

                    #Check if this tweet exists in the list
                    if hashlib.md5(tw.description.encode()).hexdigest() not in tweets.keys():
                        tweets[hashlib.md5(tw.description.encode()).hexdigest()] = tw
                        tweets_growing = True

                #Scroll down to find more tweets
                elem = self.driver.find_element_by_tag_name("body")
                elem.send_keys(Keys.END)
                sleep(SCROLL_PAUSE_TIME)

            return list(tweets.values())