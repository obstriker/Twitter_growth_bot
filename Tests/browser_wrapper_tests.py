import unittest
import sys
sys.path.insert(0,'..')
from twitter_browser_wrapper import *
from config import *

class browser_wrapper_test(unittest.TestCase):
    def test_twitter_follow(self):
        TEST_FOLLOWEE = "DouglasBShaw"

        t = twitter_browser_wrapper()
        t.login(TEST_USERNAME, TEST_PASSWORD)
        if t._twitter_browser_wrapper__check_for_login_indicator("ohad02457744"):
            t.follow(TEST_FOLLOWEE)
        
        self.assertEqual(t.am_i_following(TEST_FOLLOWEE))
            
        t.driver.quit()

    def test_twitter_unfollow(self):
        TEST_FOLLOWEE = "DouglasBShaw"

        t = twitter_browser_wrapper()
        t.login(TEST_USERNAME, TEST_PASSWORD)
        if t._twitter_browser_wrapper__check_for_login_indicator(TEST_USERNAME):
            t.unfollow(TEST_FOLLOWEE)
        
        self.assertEqual(t.am_i_following(TEST_FOLLOWEE) == False)
        

    def test_twitter_login(self):
        t = twitter_browser_wrapper()
        t.login(TEST_USERNAME, TEST_PASSWORD)
        self.assertEqual(t._twitter_browser_wrapper__check_for_login_indicator(TEST_USERNAME))
        
    def test_twitter_tweet(self):
        t = twitter_browser_wrapper()
        t.login(TEST_USERNAME, TEST_PASSWORD)
        t.tweet("Hello world!")
        sleep(1)

        my_tweets = t.get_username_tweets()
        self.assertEqual(my_tweets)
        self.assertEqual(my_tweets[-1] == "Hello world!")


    def test_twitter_find_followers(self):
        t = twitter_browser_wrapper()
        t.login(TEST_USERNAME, TEST_PASSWORD)
        #tsc = twitter_user_scrape_classes(t.driver)

        followers = t.get_username_followers(TEST_USERNAME2)

        self.assertEqual(len(followers) > 10)
        
        for follower in followers:
            print(follower.__dict__)


    def test_twitter_find_following():
        t = twitter_browser_wrapper()
        t.login(TEST_USERNAME, TEST_PASSWORD)
        #tsc = twitter_user_scrape_classes(t.driver)

        following = t.get_username_followings(TEST_USERNAME2, limit=40)
        self.assertEqual(len(following) > 10)
        
        for followee in following:
            print(followee.__dict__)

    def test_twitter_search_tweets(self):
        t = twitter_browser_wrapper()
        t.login(TEST_USERNAME, TEST_PASSWORD)
        
        tweets = t.search_tweets("#log4j")
        
        self.assertEqual(len(tweets) > 4)
        
        for tweet in tweets:
            print(tweet.__dict__)

    def test_twitter_search_username_tweets(self):
        t = twitter_browser_wrapper()
        t.login(TEST_USERNAME, TEST_PASSWORD)
        
        tweets = t.get_username_tweets("ShadoWhisper1")
        self.assertEqual(len(tweets) > 1)
        
        for tweet in tweets:
            print(tweet.__dict__)

if __name__ == '__main__':
    unittest.main()