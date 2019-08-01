###############################################################################
# Program : stream_tweets.py
# Descriptions: Used to fetch tweets based on list of search keywords
# Author : Dinesh Babu Rengasamy
###############################################################################


###############################################################################
# Required Packages
#   Make sure to use 'pip install' 
#       to install required packages for your python runtime
#   E.g., to install ElasticSearch Python API, 
#       'pip install elasticsearch' from cmd/shell
#        and to install Twitter Python API, use 'pip install tweepy'
###############################################################################
from elasticsearch import Elasticsearch
import tweepy

import json
###############################################################################


###############################################################################
# Configurations
###############################################################################

# TWITTER
#   Follow, https://apps.twitter.com/
#   A Twitter app has to be created to get the following keys
TWITTER_APP_KEYS = {
    "consumer_key": "<twitter_app_consumer_key>"
    "consumer_secret": "<twitter_app_consumer_secret>"
    "access_token": "<twitter_app_access_token>"
    "access_token_secret": "<twitter_app_access_token_secret>"
}
# Twitter keywords to listen to
#   E.g., [
#     "kerala flood",
#     "kerala sos",
#     "kerala rain",
#     "kerala rescue",
#     "kerala relief",
#   ]
LISTEN_KEYWORDS = [
    
]

# ElasticSearch
# E.g., http://10.0.0.1:9200
ES_HOST = "http://<ip_address:port>"
# Credentials to connect to the above ES server
#   Make sure the credentials have enough rights to manipulate indices
ES_CREDENTIALS = {
    "username": "<es_username>", # replace username here E.g., "admin"
    "password": "<es_password>"  # replace password here
}   
# Index is like a topic, or database name in elasticsearch
#   to add documents(tweets as json) into it 
ES_INDEX_NAME = "<index_name_to_put_tweets>"
# To delete and create the above index
#    if this is changed to False, tweets will be appended to
ES_DELETE_AND_CREATE_INDEX = True

# ********************* Do not change this *********************
#   This says what we need in the tweet
ES_TWEET_MAPPING = {
    "timestamp" : {"type" : "date"},
    "full_text": {
        "type": "text",
        "fields": {
            "english": { 
              "type":     "text",
              "analyzer": "english",
                "fielddata": "true"
            },
            "keyword": {
                "type": "keyword"
            }
        }
    },
    "mentions": {
        "type": "text",
        "fields": {
            "keyword": {
                "type": "keyword",
                "ignore_above": 256
            }
        }
    },
    "location": {
        "type": "text",
        "fields": {
            "keyword": {
                "type": "keyword",
                "ignore_above": 256
            }
        }
    },
    "screen_name": {
        "type": "text",
        "fields": {
            "keyword": {
                "type": "keyword",
                "ignore_above": 256
            }
        }
    },
    "name": {
        "type": "text",
        "fields": {
            "keyword": {
                "type": "keyword",
                "ignore_above": 256
            }
        }
    },
    "hashtags": {
        "type": "text",
        "fields": {
            "keyword": {
                "type": "keyword",
                "ignore_above": 256
            }
        }
    },
    "retweeted": {
        "type": "boolean"
    },
    "is_retweeted_status": {
        "type": "boolean"
    },
    "retweeted_screen_name":{
        "type": "text",
        "fields": {
            "keyword": {
                "type": "keyword",
                "ignore_above": 256
            }
        }
    },
    "retweeted_name":{
        "type": "text",
        "fields": {
            "keyword": {
                "type": "keyword",
                "ignore_above": 256
            }
        }
    },
    "retweeted_user_followers":{
        "type": "long"
    },
    "created_at": {
        "type": "date",
        "format": "EEE MMM dd HH:mm:ss Z yyyy"
    },
    "is_geo_enabled": {
        "type": "boolean"
    },
    "coordinates": {
      "type": "geo_point"
    }
}
###############################################################################


###############################################################################
# Components
###############################################################################
class TwitterStdOutListener(tweepy.StreamListener):

    def on_data(self, data):
        doc = json.loads(data)
        
        # parsing twitter to get require fields
        try:   
            tweet = (doc["extended_tweet"]["full_tweet"] 
                if "extended_tweet" in doc.keys() 
                else doc["retweeted_status"]["extended_tweet"]["full_text"])
        except:
            tweet = doc["text"]
        mentions_array = []
        for user_mention in doc['entities']["user_mentions"]:
        hashtags_array = []
        for hashtag in doc['entities']["hashtags"]:
            hashtags_array.append(hashtag["text"])
        
        # indexing into ElasticSearch the doc having tweets
        es.index(
            index=ES_INDEX_NAME,
            doc_type = "tweets",
            body = {
                "timestamp": doc["timestamp_ms"],
                "full_text": tweet,
                "mentions": mentions_array,
                "location": doc["user"]["location"],
                "name": doc["user"]["name"],
                "screen_name": doc["user"]['screen_name'],
                "hashtags": hashtags_array,
                "retweeted": doc["retweeted"],

                "is_retweeted_status": True 
                    if "retweeted_status" in doc.keys() else False,

                "retweeted_screen_name": 
                    doc["retweeted_status"]["user"]["screen_name"]
                        if "retweeted_status" in doc.keys() else None,

                "retweeted_name": doc["retweeted_status"]["user"]["name"] 
                    if "retweeted_status" in doc.keys() else None,

                "retweeted_user_followers": 
                    doc["retweeted_status"]["user"]["followers_count"]
                        if "retweeted_status" in doc.keys() else None,

                "created_at": doc["created_at"],
                "is_geo_enabled": doc["user"]["geo_enabled"],
                "coordinates": doc["coordinates"]
            }
        )
        # print(doc if doc["user"]["geo_enabled"] == True else None)

    def on_error(self, status_code):
        print('Got an error with status code: ' + str(status_code))
        return True # To continue listening

    def on_timeout(self):
        print('Timeout...')
        return True # To continue listening
###############################################################################


###############################################################################
# Helpers
###############################################################################
def create_index(index_name, mapping = None):
    """
    Deletes and creates ElasticSearch index with a given name,
        optionally with a mapping
    
    Arguments:
    index_name -- Name of the index to be overwriten or created
    mapping -- Optinal. Mapping to be added to the index created
    
    Returns:
    None
    """
    es.indices.delete(index=index_name)
    es.indices.create(index=index_name)
    if mapping is not None:
        es.indices.put_mapping("tweets", {'properties': mapping}, [index_name])
###############################################################################

###############################################################################
# Main Function
###############################################################################
if __name__ == '__main__':

    try:
        # Connecting to elastic search
        es = Elasticsearch("<elastic_search_ip>", 
            http_auth=("<username>", "<username>"))
        # Creating index if required based on do_overwrite setting
        if do_overwrite:
            create_index(ES_INDEX_NAME, ES_TWEET_MAPPING)

        twitter_listener = TwitterStdOutListener()
        twitter_auth = tweepy.OAuthHandler(
            TWITTER_APP_KEYS["consumer_key"], 
            TWITTER_APP_KEYS["consumer_secret"]
        )
        twitter_auth.set_access_token(
            TWITTER_APP_KEYS["access_token"], 
            TWITTER_APP_KEYS["access_token_secret"]
        )

        print("Starting twitter stream...")
        while True:
            try:
                stream = tweepy.Stream(twitter_auth, twitter_listener)
                stream.filter(track=LISTEN_KEYWORDS)
            except Exception as e:
                print("error ", e)
                continue
    except:
        print("Exception in main function", e)
        pass
###############################################################################




