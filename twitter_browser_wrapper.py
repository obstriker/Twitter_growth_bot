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

class tweet:
    def __init__():
        self.poster = ""
        self.date = ""
        self.description = ""
        self.likes = 0
        self.retweets = 0
        self.comments = 0


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
        follow_btn_opponents = None

        # Check if this works
        follow_btn_opponents = self.driver.find_elements_by_xpath("//div[contains(., 'Follow')]")
        if follow_btn_opponents:
            for follow_btn in follow_btn_opponents:
                if follow_btn.get_attribute("aria-label") == ("Follow @" + username):
                    follow_btn.click()
                    return True

    def unfollow(self, username):
        self.driver.get(TWITTER_BASE_URL + username)
        unfollow_btn_opponents = None

        # Check if this works
        unfollow_btn_opponents = self.driver.find_elements_by_xpath("//div[contains(., 'Following')]")
        if unfollow_btn_opponents:
            for unfollow_btn in unfollow_btn_opponents:
                if unfollow_btn.get_attribute("aria-label") == ("Following @" + username):
                    unfollow_btn.click()
                    return True

    def tweet(self, tweet):
        self.driver.get(TWITTER_HOMEPAGE_URL)

        #Beaware this could be chaged and get broken!
        tweet_text_area = self.driver.find_elements_by_class_name("public-DraftStyleDefault-block")
        if tweet_text_area:
            tweet_text_area = tweet_text_area[0]
            tweet_text_area.click()

        body = self.driver.find_element_by_tag_name("body")
        body.send_keys(tweet)

        tweet_btn_opponents = self.driver.find_elements_by_xpath("//div[contains(., 'Tweet')]")
        if tweet_btn_opponents:
            for tweet_btn in tweet_btn_opponents:
                if tweet_btn.get_attribute("data-testid") == "tweetButtonInline":
                    tweet_btn.click()
                    return True


    def get_feed(self):
        pass

    def get_username_tweets(self, username):
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
    if t._twitter_browser_wrapper__check_for_login_indicator():
        t.unfollow(TEST_FOLLOWEE)
        return not t.am_i_following(TEST_FOLLOWEE)

def test_twitter_login():
    t = twitter_browser_wrapper()
    t.login(TEST_USERNAME, TEST_PASSWORD)
    if t._twitter_browser_wrapper__check_for_login_indicator():
        logging.log("TEST_LOGIN: SUCCESS!")
        return True
    else:
        logging.log("TEST_LOGIN: HAS FAILED!")
        return False

def test_twitter_tweet():
    t = twitter_browser_wrapper()
    t.login(TEST_USERNAME, TEST_PASSWORD)
    t.tweet("Hello world!")
    sleep(1)

    my_tweets = t.get_username_tweets()
    if my_tweets:
        if my_tweets[-1] == "Hello world!":
            logging.log("TEST_TWEET: SUCCESS!")
            return True
        else:
            logging.log("TEST_TWEET: FAIL!")
            return False



#test_twitter_login() #Works!
#test_twitter_follow() #Works!
#test_twitter_unfollow() - unchecked
#test_twitter_tweet() #Works! test might not show real results because there is no way to check if it worked for now.