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
from twitterdb import *
from config import *
import random

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

def random_sleep(sleep_time):
    return sleep(random.uniform(sleep_time * 0.8, sleep_time * 1.2))

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

        if 'aria-label="Direct Messages"' in self.driver.page_source:
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

    def manual_login(self, username, password, saved_cookies_only = False):
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

        if saved_cookies_only:
            return False

        print("Please login manually in order to begin.")
        print("Login details are: {0}:{1}".format(username, password))
        ans = input("To manually login press 'y': ")

        if ans != 'y':
            return False
        input("Press enter when manual login has completed..")
        self._twitter_browser_wrapper__save_cookies(COOKIE_FILENAME_FORMAT.format(username))
            
        return self.manual_login(username, password, saved_cookies_only = True)
            
            

# minimum activities
# limit feature
# scrolling
# dont follow previously followed people
# 
# Future:
# human-like behaviour (scrolling, clickling, pause times)
    def follow_his_followers(self, username, limit = MAX_FOLLOW_HIS_FOLLOWERS):
        if not self.logged_in:
             return []
         
        orig_limit = limit
        self.driver.get(USERNAME_FOLLOWERS_URL.format(username))
        follow_btn_opponents = None
        followees_growing = True

        random_sleep(2)
         
        while followees_growing and limit > 0:
            followees_growing = False
            follow_btn_opponents = self.driver.find_elements_by_xpath("//div[contains(., 'Follow')]")

            for follow_btn in follow_btn_opponents:
                if limit < 1:
                    break
                try:
                    if "Follow @" not in str(follow_btn.get_attribute("aria-label")):
                        continue
                
                    username = follow_btn.get_attribute("aria-label").split("@")[1]

                    if username_followed_before(self.registered_user, username):
                        continue

                    if username == self.registered_user.username:
                            continue
                    
                    
                # follow username
                    follow_btn.click()
                    limit -= 1
                    
                # create follow record & followees_growing = True
                    log_action("follow", self.registered_user, username)

                    followees_growing = True
                    random_sleep(FOLLOW_COOLDOWN)
                except:
                    continue

            #Scroll down to find more tweets
            elem = self.driver.find_element_by_tag_name("body")
            elem.send_keys(Keys.END)
            random_sleep(SCROLL_PAUSE_TIME)
            
        return orig_limit - limit

    def unfollow(self, username_to_unfollow):
        if not self.logged_in:
             return []
                
        if self.driver.current_url != USERNAME_FOLLOWING_URL:
            self.driver.get(USERNAME_FOLLOWING_URL)
                
        unfollow_btn_opponents = None
        unfollowees_growing = True

        random_sleep(2)

        highest_unfollow_btns = 0

        while unfollowees_growing:
            unfollowees_growing = False
            unfollow_btn_opponents = self.driver.find_elements_by_xpath("//div[contains(., 'Follow')]")

            if len(unfollow_btn_opponents) > highest_unfollow_btns:
                highest_unfollow_btns = len(unfollow_btn_opponents)
                unfollowees_growing = True
            
            for unfollow_btn in unfollow_btn_opponents:
                try:
                    if "Following @" not in str(unfollow_btn.get_attribute("aria-label")):
                        continue
                
                    discovered_username = unfollow_btn.get_attribute("aria-label").split("@")[1]
                    
                    if discovered_username != username_to_unfollow:
                        continue
                    
                    # follow username
                    unfollow_btn.click()
                    random_sleep(0.5)
                    elem = self.driver.find_element_by_tag_name("body")
                    elem.send_keys(Keys.TAB)
                    random_sleep(0.5)
                    elem.send_keys(Keys.TAB)
                    random_sleep(0.5)
                    elem.send_keys(Keys.ENTER)
                    random_sleep(0.5)
                    
                    # create follow record & followees_growing = True
                    log_action("unfollow", self.registered_user, discovered_username)
                    print("unfollowed {0}".format(discovered_username))
                    return True

                except:
                    continue

            #Scroll down to find more tweets
            elem = self.driver.find_element_by_tag_name("body")
            elem.send_keys(Keys.END)
            random_sleep(SCROLL_PAUSE_TIME)

    def unfollow_batch(self, usernames_to_unfollow):
        if not self.logged_in or \
            not usernames_to_unfollow:
             return []
        
        if self.driver.current_url != USERNAME_FOLLOWING_URL.format(username):
            self.driver.get(USERNAME_FOLLOWING_URL.format(username))
                
        unfollow_btn_opponents = None
        unfollowees_growing = True

        random_sleep(2)

        highest_unfollow_btns = 0

        while unfollowees_growing:
            unfollowees_growing = False
            unfollow_btn_opponents = self.driver.find_elements_by_xpath("//div[contains(., 'Follow')]")

            if len(unfollow_btn_opponents) > highest_unfollow_btns:
                highest_unfollow_btns = len(unfollow_btn_opponents)
                unfollowees_growing = True
        
            for unfollow_btn in unfollow_btn_opponents:
                try:
                    if "Following @" not in str(unfollow_btn.get_attribute("aria-label")):
                        continue
            
                    discovered_username = unfollow_btn.get_attribute("aria-label").split("@")[1]

                    if discovered_username not in usernames_to_unfollow:
                        continue

                    # follow username
                    unfollow_btn.click()
                    random_sleep(0.5)
                    elem = self.driver.find_element_by_tag_name("body")
                    elem.send_keys(Keys.TAB)
                    random_sleep(0.5)
                    elem.send_keys(Keys.TAB)
                    random_sleep(0.5)
                    elem.send_keys(Keys.ENTER)
                    random_sleep(0.5)

                    # create follow record & followees_growing = True
                    log_action("unfollow", self.registered_user, discovered_username)
                    print("unfollowed {0}".format(discovered_username))

                    random_sleep(1.2)
                except:
                    continue
                
            #Scroll down to find more tweets
            elem = self.driver.find_element_by_tag_name("body")
            elem.send_keys(Keys.END)
            random_sleep(SCROLL_PAUSE_TIME)

    def get_users_from_hashtag_undetected(self, hashtag, limit = MAX_USERS_FROM_HASHTAG):
            scraped_users = []
            mentions_growing = True
        
            if not self.logged_in:
                return []
            
            random_sleep(4.2)
            self.driver.get(TWITTER_SEARCH_URL.format(urllib.parse.quote(hashtag)))
                
            random_sleep(3.2)

            while mentions_growing and len(scraped_users) < limit:
                mentions_growing = False
                mentions = list(set(re.findall("@\w+", self.driver.page_source)))
                if not mentions:
                    continue

                if len(mentions) + len(scraped_users) > limit:
                    mentions = mentions[: limit - len(scraped_users)]
                
                users_before = len(scraped_users)
                scraped_users += mentions
                scraped_users = list(set(scraped_users))

                if len(scraped_users) > users_before:
                    mentions_growing = True

                #Scroll down to find more tweets
                elem = self.driver.find_element_by_tag_name("body")
                elem.send_keys(Keys.END)
                random_sleep(SCROLL_PAUSE_TIME)

            return list(map(lambda user: user.replace("@",""), scraped_users))


#t = twitter_browser_wrapper()
#t.login("ShadoWhisper1", "Aa123456")
#t.login(TEST_USERNAME, TEST_PASSWORD)
#t.follow_his_followers("discord", limit = 20)
#t.unfollow_his_followers("discord")
#t.get_users_from_hashtag("#reversing")
#t.unfollow("nabil_hedar")
#t.unfollow("AccidentalCISO")