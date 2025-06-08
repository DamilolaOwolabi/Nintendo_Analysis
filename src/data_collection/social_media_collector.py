import os
import tweepy
import praw
from datetime import datetime, timedelta
import json
from typing import Dict, List
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SocialMediaCollector:
    def __init__(self):
        load_dotenv()
        self.setup_twitter_api()
        self.setup_reddit_api()
        self.base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw')

    def setup_twitter_api(self):
        """Initialize Twitter API client"""
        try:
            auth = tweepy.OAuthHandler(
                os.getenv('TWITTER_API_KEY'),
                os.getenv('TWITTER_API_SECRET')
            )
            auth.set_access_token(
                os.getenv('TWITTER_ACCESS_TOKEN'),
                os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            )
            self.twitter_api = tweepy.API(auth)
            logger.info("Twitter API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {str(e)}")
            self.twitter_api = None

    def setup_reddit_api(self):
        """Initialize Reddit API client"""
        try:
            self.reddit_api = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT')
            )
            logger.info("Reddit API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit API: {str(e)}")
            self.reddit_api = None

    def collect_twitter_data(self, query: str, days: int = 30) -> List[Dict]:
        """
        Collect tweets related to Nintendo price increase
        """
        if not self.twitter_api:
            logger.error("Twitter API not initialized")
            return []

        tweets = []
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Search tweets
            for tweet in tweepy.Cursor(
                self.twitter_api.search_tweets,
                q=query,
                lang="en",
                tweet_mode="extended",
                since=start_date.strftime('%Y-%m-%d')
            ).items(1000):  # Limit to 1000 tweets
                
                tweet_data = {
                    'id': tweet.id,
                    'created_at': tweet.created_at.isoformat(),
                    'text': tweet.full_text,
                    'user': {
                        'id': tweet.user.id,
                        'name': tweet.user.name,
                        'followers_count': tweet.user.followers_count
                    },
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count
                }
                tweets.append(tweet_data)
                
            logger.info(f"Collected {len(tweets)} tweets")
            return tweets
            
        except Exception as e:
            logger.error(f"Error collecting Twitter data: {str(e)}")
            return []

    def collect_reddit_data(self, subreddits: List[str], query: str, days: int = 30) -> List[Dict]:
        """
        Collect Reddit posts and comments related to Nintendo price increase
        """
        if not self.reddit_api:
            logger.error("Reddit API not initialized")
            return []

        posts = []
        try:
            for subreddit_name in subreddits:
                subreddit = self.reddit_api.subreddit(subreddit_name)
                
                # Search for posts
                for post in subreddit.search(query, limit=100):
                    post_data = {
                        'id': post.id,
                        'title': post.title,
                        'created_utc': post.created_utc,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'subreddit': subreddit_name,
                        'comments': []
                    }
                    
                    # Get comments
                    post.comments.replace_more(limit=0)  # Limit to top-level comments
                    for comment in post.comments:
                        comment_data = {
                            'id': comment.id,
                            'body': comment.body,
                            'score': comment.score,
                            'created_utc': comment.created_utc
                        }
                        post_data['comments'].append(comment_data)
                    
                    posts.append(post_data)
                
            logger.info(f"Collected {len(posts)} Reddit posts")
            return posts
            
        except Exception as e:
            logger.error(f"Error collecting Reddit data: {str(e)}")
            return []

    def save_data(self, data: List[Dict], platform: str, query: str):
        """
        Save collected social media data to JSON file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{platform}_{query.replace(' ', '_')}_{timestamp}.json"
        filepath = os.path.join(self.base_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Data saved to {filepath}")

def main():
    collector = SocialMediaCollector()
    
    # Collect Twitter data
    twitter_query = "nintendo price increase OR nintendo $90 OR nintendo switch 2 price"
    twitter_data = collector.collect_twitter_data(twitter_query)
    collector.save_data(twitter_data, 'twitter', twitter_query)
    
    # Collect Reddit data
    subreddits = ['NintendoSwitch', 'gaming', 'nintendo']
    reddit_query = "nintendo price increase OR nintendo $90 OR nintendo switch 2 price"
    reddit_data = collector.collect_reddit_data(subreddits, reddit_query)
    collector.save_data(reddit_data, 'reddit', reddit_query)

if __name__ == "__main__":
    main() 