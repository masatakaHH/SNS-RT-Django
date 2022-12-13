import tweepy
from decouple import config
from config import settings
import requests
import json

class TwitterAPI:
    def __init__(self):
        self.bearer_token = settings.bearer_token
        self.api_key = settings.api_key
        self.api_secret = settings.api_secret
        self.client_id = settings.client_id
        self.client_secret = settings.client_secret
        self.oauth_callback_url = settings.oauth_callback_url

    def twitter_login(self):
        oauth1_user_handler = tweepy.OAuthHandler(self.api_key, self.api_secret, callback=self.oauth_callback_url)
        url = oauth1_user_handler.get_authorization_url(signin_with_twitter=True)
        request_token = oauth1_user_handler.request_token["oauth_token"]
        request_secret = oauth1_user_handler.request_token["oauth_token_secret"]
        return url, request_token, request_secret

    def twitter_callback(self,oauth_verifier, oauth_token, oauth_token_secret):
        oauth1_user_handler = tweepy.OAuthHandler(self.api_key, self.api_secret, callback=self.oauth_callback_url)
        oauth1_user_handler.request_token = {
            'oauth_token': oauth_token,
            'oauth_token_secret': oauth_token_secret
        }
        access_token, access_token_secret = oauth1_user_handler.get_access_token(oauth_verifier)
        return access_token, access_token_secret

    def client_init(self, access_token, access_token_secret):
        try:
            client = tweepy.Client(consumer_key=self.api_key, consumer_secret=self.api_secret, access_token=access_token,access_token_secret=access_token_secret)
            return client
        except Exception as e:
            print(e)
            return None
        
    def api_init(self, access_token, access_token_secret):
        try:
            auth = tweepy.OAuthHandler(consumer_key=self.api_key, consumer_secret=self.api_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)
            return api
        except Exception as e:
            print(e)
            return None
    
    def get_user(self, client, id):
        try:
            info = client.get_user(user_auth=True,id=id,expansions='pinned_tweet_id',user_fields=['profile_image_url'])
            return info
        except Exception as e:
            print(e)
            return None
    
    def get_me(self, client):
        try:
            info = client.get_me(user_auth=True,expansions='pinned_tweet_id',user_fields=['public_metrics','profile_image_url','protected','location','entities','withheld','verified'])
            return info
        except Exception as e:
            print(e)
            return None
    
    def get_users_followers(self, id, client,max_results=None,pagination_token=None):
        try:
            followers_info = client.get_users_followers(user_auth=True,id=id,max_results=max_results,pagination_token=pagination_token,user_fields=['profile_image_url'])
            return followers_info
        except Exception as e:
            print(e)
            return None
        
    def get_users_following(self, id, client,max_results=None,pagination_token=None):
        try:
            following_info = client.get_users_following(user_auth=True,id=id, max_results=max_results, pagination_token=pagination_token,user_fields=['profile_image_url'])
            return following_info
        except Exception as e:
            print(e)
            return None
        
    def get_users_following_ids(self, id, client,max_results=None,pagination_token=None):
        try:
            following_info = client.get_users_following(user_auth=True,id=id, max_results=max_results, expansions='pinned_tweet_id',pagination_token=pagination_token,user_fields=['id'])
            return following_info
        except Exception as e:
            print(e)
            return None
        
    def get_liking_users(self, tweet_id, client):
        try:
            liking_users = client.get_liking_users(user_auth=True,id=tweet_id)
            return liking_users
        except Exception as e:
            return None
        
    def get_liked_tweets(self, id, client):
        try:
            liked_tweeks = client.get_liked_tweets(user_auth=True,id=id)
            return liked_tweeks
        except Exception as e:
            return None
        
    def get_users_tweets(self, id, client,max_result,end_time=None,start_time=None):
        try:
            liked_tweeks = client.get_users_tweets(user_auth=True,id=id,max_results=max_result,end_time=end_time,start_time=start_time)
            return liked_tweeks
        except Exception as e:
            return None
        
    def get_users_retweets(self, id, client,max_result,end_time=None,start_time=None):
        try:
            liked_tweeks = client.get_users_tweets(user_auth=True,id=id,max_results=max_result,exclude=['retweets','replies'],end_time=end_time,start_time=start_time)
            return liked_tweeks
        except Exception as e:
            return None
        
    def get_blocked(self, client):
        try:
            _blocked = client.get_blocked(user_auth=True)
            return _blocked
        except Exception as e:
            return None
        
    def get_recent_tweets_count(self,client,query,end_time=None,start_time=None):
        try:
            recent_tweets_count = client.get_recent_tweets_count(query,end_time=end_time,start_time=start_time,user_auth=True)
            return recent_tweets_count
        except Exception as e:
            return None
        
    def search_recent_tweets(self,client,query,max_results=None,next_token=None,sort_order=None):
        try:
            recent_tweets_count = client.search_recent_tweets(query,max_results=max_results,next_token=next_token,sort_order=sort_order,user_auth=True)
            return recent_tweets_count
        except Exception as e:
            return None
    
    def get_home_timeline(self,client,max_results=None,next_token=None):
        try:
            recent_tweets = client.get_home_timeline(user_auth=True,max_results=max_results,pagination_token=next_token,expansions='attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id',user_fields='created_at,description,name,profile_image_url,url,username')
            return recent_tweets
        except Exception as e:
            return None
        