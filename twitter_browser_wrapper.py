# This module handles the selenium browser and navigates to do simple jobs at the twitter page.
# This module aims to be generic enough to handle Twitter webpage changes in the future.

# TODO: refactor to avoid crashes
# Last test not working, produces the same results everytime
# Last context: tried to implement search_tweets

# This module has class for tweets and user
# Each class know how to scrape objects statically (to obtain class names)
# And then you can use it to find relatively. for example search for a tweet that i
# know all it's details and I search for the details. then I accuire the class names 
# and use it to scrape these objects later.
# This mechanism built to avoid anti-scraping (scrambling class names or ids)

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import os
import logging
import pickle
from time import sleep
import re
import urllib

TWITTER_BASE_URL = "https://mobile.twitter.com/"
TWITTER_SIGN_IN_URL = "https://mobile.twitter.com/i/flow/login"
TWITTER_HOMEPAGE_URL = "https://mobile.twitter.com/"
TWITTER_SEARCH_URL = "https://twitter.com/search?q={0}&src=typed_query&f=live"
TEST_USERNAME = "ohad02457744"
TEST_USERNAME2 = "Sanrio_OTD"
TEST_PASSWORD = "ohadva12"
COOKIE_FILENAME_FORMAT = "user_{0}.pkl"
USERNAME_FOLLOWERS_URL = "https://twitter.com/{0}/followers"
USERNAME_FOLLOWING_URL = "https://twitter.com/{0}/following"

opts = Options()
opts.headless = False

class twitter_user:
    def __init__(self):
        self.follower_count = 0
        self.username = ""
        self.followers = []
        self.tweets = []
        self.following = []


class twitter_user_scrape_classes:
    def __init__(self, driver):
        self.driver = driver
        self.follower_count = ""
        self.username = ""
        self.followers = ""
        self.following = ""
        self.tweets = ""


#Another way to implement this is by using dictionary and counting which class has the most objects
# This indicates on the Follow buttons on the followers 
    def find_static_followers_class(self, username = TEST_USERNAME2):
        self.driver.get(USERNAME_FOLLOWERS_URL.format(username))
        sleep(4)
        followers = self.driver.find_elements_by_xpath("//span[contains(., '@')]")
        username_pattern = re.compile(r"@\w+")

        for follower in followers:
            if username_pattern.match(follower.get_attribute("innerText")):             
                while follower.tag_name != "html" and follower.get_attribute("data-testid") != "UserCell":
                    follower = follower.find_element_by_xpath("..")
            
                if follower.get_attribute("data-testid") == "UserCell":
                    self.followers = follower.get_attribute("class")
                    return self.followers

    def find_static_following_class(self):
        self.driver.get(USERNAME_FOLLOWING_URL.format(TEST_USERNAME2))
        sleep(4)
        following = self.driver.find_elements_by_xpath("//span[contains(., '@')]")
        username_pattern = re.compile(r"@\w+")

        for followee in following:
            if username_pattern.match(followee.get_attribute("innerText")):             
                while followee.tag_name != "html" and followee.get_attribute("data-testid") != "UserCell":
                    followee = followee.find_element_by_xpath("..")
            
                if followee.get_attribute("data-testid") == "UserCell":
                    self.following = followee.get_attribute("class")
                    return self.following

    #TODO: extend to include all followers
    def find_relative_following_class(self, username):
        extracted_followees = []
        username_pattern = re.compile(r"@\w+")
        following = self.driver.find_elements_by_xpath("//div[@class='"+ self.following +"']")

        for followee in following:
            lines = followee.get_attribute("innerText").split("\n")
            for line in lines:
                if username_pattern.match(line):
                    extracted_followees.append(line)
                    break

        return extracted_followees

    #TODO: extend to include all followers
    def find_relative_followers_class(self, username):
        extracted_followers = []
        username_pattern = re.compile(r"@\w+")
        followers = self.driver.find_elements_by_xpath("//div[@class='"+ self.followers +"']")

        for follower in followers:
            lines = follower.get_attribute("innerText").split("\n")
            for line in lines:
                if username_pattern.match(line):
                    extracted_followers.append(line)
                    break

        return extracted_followers

class tweet:
    def __init__(self):
        self.username = ""
        self.date = ""
        self.description = ""
        self.likes = 0
        self.retweets = 0
        self.comments = 0

class tweet_scrape_classes:
    def __init__(self, driver):
        self.driver = driver
        self.follower = ""
        self.following = ""
        self.block = ""
        self.username = ""
        self.date = ""
        self.description = ""
        self.likes = ""
        self.retweets = ""
        self.comments = ""



    def find_static_username_class(self, username):
        usernames = self.driver.find_elements_by_xpath("//span[contains(., '"+ username +"')]")
        
        for user in usernames:
            if user.get_attribute("innerText") == username:
                self.username = user.get_attribute("class")
                return (self.username, user)
                
    def find_relative_username(self, article):
        usernames = article.find_elements_by_xpath("//span[@class='"+ self.username +"']")

        for username in usernames:
            if "@" in  username.get_attribute("innerText"):
                return username.get_attribute("innerText")

        return username
        
    def find_relative_date(self, article):
        try:
            date = article.find_element_by_tag_name("time")
            return date.get_attribute("innerText")
        except:
            return ""

    def find_relative_description(self, article):
        description = article.find_element_by_xpath("//div[@class='"+ self.description +"']")
        return description.get_attribute("innerText")

    def find_relative_blocks(self):
        if self.block:
            articles = self.driver.find_elements_by_xpath("//article[@class='"+ self.block +"']")
            return articles
        else:
            #TODO: Run find_static_block in other tab and close it
            pass

    def find_static_time_class(self):
        dates = self.driver.find_elements_by_xpath("//time[contains(., 'Dec 12')]")
        for date in dates:
            if date.get_attribute("innerText") == "Dec 12":
                self.date = date.get_attribute("class")
                return self.date

    def find_static_description_class(self):
        articles = self.find_relative_blocks()

        for article in articles:
            descriptions = article.find_elements_by_xpath("//div[contains(., ' for Log4shell')]")

            for description in descriptions:
                if description.get_attribute("innerText") == "Vaccine for Log4shell\n#log4j #Log4Shell":
                    if len(description.get_attribute("class")) > len(self.description):
                        self.description = description.get_attribute("class")
            return (self.description, description)

    def find_static_block(self, initial=True):
        article = None

        if initial:
            self.driver.get(TWITTER_SEARCH_URL.format("\"vaccine\" (from:Shadowhisper1)"))
            sleep(3)
            username = self.find_static_username_class("@ShadoWhisper1")
            article = username[1]

            while article.tag_name != "article":
                article = article.find_element_by_xpath("..")

            self.block = article.get_attribute("class")
            return self.block

    #TODO: fix description fetching, try to fetch lines until they meet regex of \n\d
    def article_to_tweet(self, article):
        t = tweet()
        text = article.get_attribute("innerText").split("\n")
        time_pattern = re.compile(r"\d+[hmdy]")
        date_pattern = re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Dec)\s\d{1,2}")
        username_pattern = re.compile(r"@\w+")
        like_pattern = re.compile(r"\n\d")

        for line in text:
            if time_pattern.match(line) or date_pattern.match(line):
                t.date = line
            elif username_pattern.match(line) and not t.username:
                t.username = line
            elif like_pattern.match(line):
                break
            elif t.username and len(line) > 5:
                t.description = t.description + " " + line
        
        #t.description = ' '.join(text[4:-2])

        return t

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
            return True
        else:
            return False

    def login(self, username, password):
        self.driver.get(TWITTER_HOMEPAGE_URL)
        if self._twitter_browser_wrapper__load_cookies(COOKIE_FILENAME_FORMAT.format(username)) \
            and self._twitter_browser_wrapper__check_for_login_indicator(username):
            self.logged_in = True
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
            return True
        else:
            self.logged_in = False
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
        return self.search_tweets("(from:{0})".format(username.replace("@","")))

    def get_hashtag_tweets(self, hashtag):
        return self.search_tweets(hashtag)

    def get_username_followers(self, username):
        extracted_followers = []

        if not self.logged_in:
             return []
        
        if not hasattr(self, 'tsc'):
            self.tsc = tweet_scrape_classes(self.driver)
            
        if not self.tsc.followers:
            self.tsc.find_static_followers_class()

        followers = tsc.find_relative_followers_class(username)

        for follower in followers:
            extracted_followers.append(follower)

        return extracted_followers

    def get_username_following(self, username):
        extracted_following = []

        if not self.logged_in:
             return []
        
        if not hasattr(self, 'tsc'):
            self.tsc = twitter_user_scrape_classes(self.driver)
            
        if not self.tsc.following:
            self.tsc.find_static_following_class()

        following = self.tsc.find_relative_following_class(username)

        for followee in following:
            extracted_following.append(followee)

        return extracted_following

        
    #TODO: how to load dynamic tweets? (click space and go down?)
    def search_tweets(self, term, limit=20):
        tweets = []

        if self.logged_in:
            if not hasattr(self, 'tsc'):
                self.tsc = tweet_scrape_classes(self.driver)
                self.tsc.find_static_block()

            self.driver.get(TWITTER_SEARCH_URL.format(urllib.parse.quote(term)))
            sleep(3)
            articles = self.tsc.find_relative_blocks()

            for article in articles:
                tweets.append(self.tsc.article_to_tweet(article))
            
            return tweets


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

def test_twitter_find_scrape_classes():
    t = twitter_browser_wrapper()
    t.login(TEST_USERNAME, TEST_PASSWORD)
    tsc = tweet_scrape_classes(t.driver)

    #First static run
    tsc.find_static_block()
    #tsc.find_static_description_class()
    #tsc.find_static_time_class()
    #tsc.find_static_username_class("@ShadoWhisper1")

    #Second - relative on dynamic page
    t.driver.get(TWITTER_SEARCH_URL.format("hello"))
    sleep(3)
    articles = tsc.find_relative_blocks()

    for article in articles:
        at = tsc.article_to_tweet(article)
        print("username: ", at.username)
        print("date: ", at.date)
        print("description: ", at.description)
        print()

def test_twitter_find_followers():
    t = twitter_browser_wrapper()
    t.login(TEST_USERNAME, TEST_PASSWORD)
    #tsc = twitter_user_scrape_classes(t.driver)

    followers = t.get_username_followers(TEST_USERNAME2)

    for follower in followers:
        print(follower.__dict__)


def test_twitter_find_following():
    t = twitter_browser_wrapper()
    t.login(TEST_USERNAME, TEST_PASSWORD)
    #tsc = twitter_user_scrape_classes(t.driver)

    following = t.get_username_following(TEST_USERNAME2)

    for followee in following:
        print(followee)

def test_twitter_search_tweets():
    t = twitter_browser_wrapper()
    t.login(TEST_USERNAME, TEST_PASSWORD)
    for tweet in t.search_tweets("#log4j"):
        print(tweet.__dict__)

def test_twitter_search_username_tweets():
    t = twitter_browser_wrapper()
    t.login(TEST_USERNAME, TEST_PASSWORD)
    for tweet in t.get_username_tweets("ShadoWhisper1"):
        print(tweet.__dict__)

    





#test_twitter_login() #Works!
#test_twitter_follow() #Works!
#test_twitter_unfollow() - unchecked
#test_twitter_tweet() #Works! test might not show real results because there is no way to check if it worked for now.
#test_twitter_find_tweets_classes()
#test_twitter_find_followers()
#test_twitter_find_following()
#test_twitter_find_following()
#test_twitter_search_tweets()
test_twitter_search_username_tweets()