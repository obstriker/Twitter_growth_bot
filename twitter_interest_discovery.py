# This module gets a username(s) and crawls through his tweets and collects hashtags.
# This module provides a few functionalities:
# 1. in: username -> out: hashtags
# 1. in: hashtag -> out: more hashtags in the same domain
# 2. in: username -> out: usernames in the same domain
# 3. in: hashtag  -> out: usernames that posted tweet with this hashtag (limited)
# 4. in: username -> out: username -> out: followers (target audience)
# 4. in: hashtag -> out: username -> out: followers (target audience)
from twitter_browser_wrapper import *
from twitterdb import *

TWEET_LIMIT = 10

class twitter_interest_discovery:
    def get_hashtags_from_user(t, user):
        hashtags = []
        for tweet in t.get_username_tweets(user):
            for word in tweet.description.split(" "):
                if "#" in word:
                    hashtags.append(word)
        return hashtags

    def get_hashtags_from_hashtag(t, hashtag, limit = 20):
        hashtags = []
        for hashtag in t.get_hashtag_tweets(hashtag, limit):
            for word in hashtag.description.split(" "):
                if "#" in word:
                    hashtags.append(word)
        return list(set(hashtags))

    def get_users_from_user(t, user):
        users = []
        hashtags = twitter_interest_discovery.get_hashtags_from_user(t, user)
        for hashtag in hashtags:
            users += twitter_interest_discovery.get_users_from_hashtag(t, hashtag)
        return list(set(users))

    def get_users_from_hashtag(t, hashtag, limit = 20):
        users = []
        for tweet in t.get_hashtag_tweets(hashtag, limit):
            users.append(tweet.user)
        return list(set(users))

    def get_users_from_hashtags(t, hashtags, limit = 100):
        users = []

        for hashtag in hashtags:
            users.append(get_users_from_hashtag(hashtag))

        return users

    def get_followers_from_hashtag(t, hashtag, limit = 100):
        followers_from_hashtag = []
        users = twitter_interest_discovery.get_users_from_hashtag(t, hashtag, limit)
        for user in users:
            followers = t.get_username_followers(user.username)
            for follower in followers:
                followers_from_hashtag.append(follower.follower.username)
        return list(set(followers_from_hashtag))

#t = twitter_browser_wrapper()
#t.login("ohad02457744", "ohadva12")
#followers = t.get_username_followers("stuarts_world_")
#followers = ['@i4cy_', '@freetobe0000', '@Pentaform', '@PieffT', '@the_gigio', '@genevasocute0', '@ham_gretsky', '@creemama', '@RecA_no_R', '@TonjaQUEST', '@Koleyayyc', '@Simply_Redman', '@CryptoNewsCAN', '@Leelar16723096', '@3WVR8WeRe850d3s', '@Ashot_', '@nkamlo06', '@GenevieDEPP', '@angela_mondou', '@sophie03832328', '@ZRH_Mike', '@Judah26i', '@vishne0', '@jeffrey48402019', '@entezar_0012', '@isc2alberta', '@ze_lama', '@assafrl', '@kann_news', '@Ashot_', '@nkamlo06', '@GenevieDEPP', '@angela_mondou', '@sophie03832328', '@ZRH_Mike', '@Judah26i', '@vishne0', '@jeffrey48402019', '@entezar_0012', '@isc2alberta', '@Changiiinterna1', '@jmeredith96', '@JCSoterasGarcia', '@Barb_Joy', '@EstherW38486319', '@SassChit', '@IreneSterian', '@mikmilli535', '@RightMinded1', '@TheUrbanAbo', '@cyber_ula', '@DijitalKirkos1', '@Women_Agents', '@mZjQfddIDIxMDOj', '@Musicpararelaxa', '@DomIsa6', '@Frank1701', '@darkflower000', '@pushkaramethi', '@tomi0871', '@ShadoWhisper1', '@systelasia', '@Spychacz2', '@AlexKzemi', '@GodoskyGentile', '@Axc7', '@tranquillarium', '@MamtaNarang', '@BlessedKFM', '@hardrock1231', '@Jumpstart_Labs', '@ze_lama', '@assafrl', '@kann_news', '@TheUrbanAbo', '@cyber_ula', '@DijitalKirkos1', '@Women_Agents', '@mZjQfddIDIxMDOj', '@Musicpararelaxa', '@DomIsa6', '@Frank1701', '@darkflower000', '@pushkaramethi', '@tomi0871', '@ShadoWhisper1', '@systelasia', '@Spychacz2', '@AlexKzemi', '@GodoskyGentile', '@Axc7', '@tranquillarium', '@MamtaNarang', '@BlessedKFM', '@hardrock1231', '@Jumpstart_Labs', '@RealtorsHelpYou', '@pwilson1328', '@XXhello03XX', '@BarleyOctavia', '@TheLastAesir', '@CryptvLtd', '@Evagirlx', '@azameth', '@DesmondSskenya', '@Goddess_anne23', '@ScaredShyGirl', '@_biersnob', '@PieterseMarc', '@Jochen_Pflesser', '@JoyBlak51319118', '@KrystianLiikka', '@ElizabethDike5', '@SELESMS', '@Harpree14944761', '@Natasha_Volana', '@ze_lama', '@assafrl', '@kann_news']
#followers = followers[0:5]
#for follower in followers:
#    t.follow(follower)
#user = User.get_or_create(username="stuarts_world_")[0]
#for follower in followers:
#    try:
#        user2 = User.get_or_create(username=follower)[0]
#        follower = Follower.get_or_create(followed=user, follower = user2)[0]
#    except:
#        continue
#    user2.save()
#    follower.save()

#print()
#followers = twitter_interest_discovery.get_followers_from_hashtag(t, "#reversing", limit = 100)
#print()

#hashtagss = twitter_intrest_discovery.getfollowersfromhashtags(t, "#reversing")
