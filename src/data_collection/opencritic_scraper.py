import csv
import os
import logging
import time
import random
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OPENCRITIC_API_URL = "https://api.opencritic.com/api/game"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw', 'nintendo_game_scores.csv')

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.68 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.68 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
    ]
    return random.choice(user_agents)

def get_headers():
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://opencritic.com',
        'Referer': 'https://opencritic.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site'
    }

def scrape_opencritic_scores():
    logger.info("Scraping OpenCritic game scores")
    
    try:
        # First, get the list of Nintendo Switch games
        params = {
            'platforms': 'switch',
            'sort': 'score',
            'order': 'desc',
            'limit': 100
        }
        
        response = requests.get(OPENCRITIC_API_URL, headers=get_headers(), params=params)
        response.raise_for_status()
        
        games = response.json()
        logger.info(f"Found {len(games)} Nintendo Switch games")
        
        data = []
        for game in games:
            try:
                # Get detailed game info
                game_id = game['id']
                game_url = f"{OPENCRITIC_API_URL}/{game_id}"
                
                # Add a small delay between requests
                time.sleep(random.uniform(0.5, 1.5))
                
                game_response = requests.get(game_url, headers=get_headers())
                game_response.raise_for_status()
                game_details = game_response.json()
                
                # Extract relevant information
                title = game_details.get('name', '')
                score = game_details.get('topCriticScore', 0)
                release_date = game_details.get('firstReleaseDate', '')
                
                # Convert release date to a more readable format
                if release_date:
                    try:
                        release_date = datetime.fromisoformat(release_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                    except:
                        release_date = ''
                
                data.append({
                    'Game': title,
                    'OpenCritic Score': score,
                    'Release Date': release_date
                })
                
                logger.info(f"Processed game: {title}")
                
            except Exception as e:
                logger.warning(f"Error processing game {game.get('name', 'unknown')}: {str(e)}")
                continue
        
        if not data:
            logger.warning('No game data found.')
            return
        
        # Save to CSV
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"Nintendo game scores saved to {OUTPUT_FILE}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request: {str(e)}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    scrape_opencritic_scores() 