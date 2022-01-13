import unittest
import sys
sys.path.insert(0,'..')
from scrape_classes import *
from config import *

class scrape_classes_tests(unittest.TestCase):
    def test_twitter_find_scrape_classes(self):
        t = twitter_browser_wrapper()
        t.login(TEST_USERNAME, TEST_PASSWORD)
        tsc = tweet_scrape_classes(t.driver)

        #First static run
        tsc.find_static_block()
        tsc.find_static_description_class()
        tsc.find_static_time_class()
        tsc.find_static_username_class("@ShadoWhisper1")

        #Second - relative on dynamic page
        t.driver.get(TWITTER_SEARCH_URL.format("hello"))
        sleep(3)
        articles = tsc.find_relative_blocks()

        self.assertEqual(len(articles) >= 1)
        
        for article in articles:
            at = tsc.article_to_tweet(article)
            print("username: ", at.username)
            print("date: ", at.date)
            print("description: ", at.description)
            
            
        t.driver.quit()

if __name__ == '__main__':
    unittest.main()