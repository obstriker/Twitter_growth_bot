from config import *
from time import sleep
import re
from twitterdb import *

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
        text = article.get_attribute("innerText").split("\n")
        time_pattern = re.compile(r"\d+[hmdy]")
        date_pattern = re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Dec)\s\d{1,2}")
        username_pattern = re.compile(r"@\w+")
        like_pattern = re.compile(r"\n\d")

        time = ""
        description = ""
        username = ""

        for line in text:
            if time_pattern.match(line) or date_pattern.match(line):
                time = line
            elif username_pattern.match(line) and not username:
                username = line.replace("@","")
            elif like_pattern.match(line):
                break
            elif username and len(line) > 5:
                description = description + " " + line
        user = User.get_or_create(username = username)[0]
        t = Tweet.get_or_create(user = user, description = description)[0]
        t.time = time

        return t
    
class scrape_class_manager:
    def __init__(self, driver):
        self.tscu = twitter_user_scrape_classes(driver)
        self.tsc = tweet_scrape_classes(driver)