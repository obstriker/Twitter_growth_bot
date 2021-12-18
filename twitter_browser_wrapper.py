# This module handles the selenium browser and navigates to do simple jobs at the twitter page.
# This module aims to be generic enough to handle Twitter webpage changes in the future.

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import os
import logging
import pickle
from time import sleep

TWITTER_BASE_URL = "https://mobile.twitter.com/"
TWITTER_SIGN_IN_URL = "https://mobile.twitter.com/i/flow/login"
TWITTER_HOMEPAGE_URL = "https://mobile.twitter.com/"
TEST_USERNAME = "ohad02457744"
TEST_PASSWORD = "ohadva12"
COOKIE_FILENAME_FORMAT = "user_{0}.pkl"

opts = Options()
opts.headless = False

class twitter_browser_wrapper:
    driver = None
    def __init__(self):
        self.driver = webdriver.Firefox(options=opts)

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
            return True
        else:
            return False

    def login(self, username, password):
        self.driver.get(TWITTER_HOMEPAGE_URL)
        if self._twitter_browser_wrapper__load_cookies(COOKIE_FILENAME_FORMAT.format(username)) \
            and self._twitter_browser_wrapper__check_for_login_indicator(username):
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
        elem.send_keys(Keys.ENTER)

        if self._twitter_browser_wrapper__check_for_login_indicator(username):
            self._twitter_browser_wrapper__save_cookies(COOKIE_FILENAME_FORMAT.format(username))
            return True
        else:
            return False

    def follow(self, username):
        self.driver.get(TWITTER_BASE_URL + username)
        follow_btn = None

        # Check if this works
        follow_btn = self.driver.find_element_by_xpath("//div[contains(., 'Follow')]")
        if follow_btn:
            follow_btn.click()

    def unfollow(self, username):
        self.driver.get(TWITTER_BASE_URL + username)
        unfollow_btn = None
        follow_btn = None
        retval = False

        # Check if this works
        # follow_btn = self.driver.find_element_by_xpath("//div[contains(., 'Follow')]")
        unfollow_btn = self.driver.find_element_by_xpath("//div[contains(., 'Following')]")
        if unfollow_btn:
            follow_btn.click()
            retval = True

        return retval

    def tweet():
        pass

    def get_feed():
        pass

    def get_username_tweets():
        pass

    def get_hashtag_tweets():
        pass

    def search_tweets():
        pass


def test_twitter_follow():
    TEST_FOLLOWEE = "DouglasBShaw"

    t = twitter_browser_wrapper()
    t.login(TEST_USERNAME, TEST_PASSWORD)
    if t._twitter_browser_wrapper__check_for_login_indicator("ohad02457744"):
        t.follow(TEST_FOLLOWEE)
        return t.am_i_following(TEST_FOLLOWEE)


def test_twitter_unfollow():
    TEST_FOLLOWEE = "DouglasBShaw"

    t = twitter_browser_wrapper()
    t.login(TEST_USERNAME, TEST_PASSWORD)
    if t.__check_for_login_indicator():
        t.unfollow(TEST_FOLLOWEE)
        return not t.am_i_following(TEST_FOLLOWEE)

def test_twitter_login():
    t = twitter_browser_wrapper()
    t.login(TEST_USERNAME, TEST_PASSWORD)
    if t.__check_for_login_indicator():
        logging.log("TEST_LOGIN: SUCCESS!")
        return True
    else:
        logging.log("TEST_LOGIN: HAS FAILED!")
        return False

#test_twitter_login() #Works!
test_twitter_follow()
test_twitter_unfollow()