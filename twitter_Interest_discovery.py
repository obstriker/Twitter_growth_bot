# This module gets a username(s) and crawls through his tweets and collects hashtags.
# This module provides a few functionalities:
# 1. in: username -> out: hashtags
# 1. in: hashtag -> out: more hashtags in the same domain
# 2. in: username -> out: usernames in the same domain
# 3. in: hashtag  -> out: usernames that posted tweet with this hashtag (limited)
# 4. in: username -> out: username -> out: followers (target audience)