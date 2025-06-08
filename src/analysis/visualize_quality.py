import csv
import os
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw', 'nintendo_game_scores.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'processed', 'visualizations')

def create_visualizations():
    logger.info("Creating visualizations for game quality data")
    
    try:
        # Read the data
        games = []
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                games.append({
                    'Game': row['Game'],
                    'Score': float(row['OpenCritic Score']),
                    'Release Date': row['Release Date']
                })
        
        if not games:
            logger.error("No game data found")
            return
        
        # Create output directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Set style
        plt.style.use('default')
        sns.set_theme()
        
        # 1. Score Distribution
        plt.figure(figsize=(10, 6))
        sns.histplot(data=[game['Score'] for game in games], bins=20, color='skyblue')
        plt.title('Distribution of Nintendo Switch Game Scores', pad=20)
        plt.xlabel('OpenCritic Score')
        plt.ylabel('Number of Games')
        plt.axvline(x=80, color='red', linestyle='--', label='High Quality Threshold (80)')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'score_distribution.png'))
        plt.close()
        
        # 2. Quality Categories
        quality_categories = {
            'High Quality (≥80)': sum(1 for game in games if game['Score'] >= 80),
            'Medium Quality (60-79)': sum(1 for game in games if 60 <= game['Score'] < 80),
            'Low Quality (<60)': sum(1 for game in games if game['Score'] < 60)
        }
        
        plt.figure(figsize=(10, 6))
        plt.pie(quality_categories.values(), 
                labels=quality_categories.keys(), 
                autopct='%1.1f%%',
                colors=['#2ecc71', '#f1c40f', '#e74c3c'])
        plt.title('Distribution of Game Quality Categories', pad=20)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'quality_categories.png'))
        plt.close()
        
        # 3. Top 10 Games
        top_10 = sorted(games, key=lambda x: x['Score'], reverse=True)[:10]
        plt.figure(figsize=(12, 6))
        bars = plt.barh([game['Game'] for game in top_10], 
                       [game['Score'] for game in top_10],
                       color='skyblue')
        plt.title('Top 10 Nintendo Switch Games by Score', pad=20)
        plt.xlabel('OpenCritic Score')
        plt.ylabel('Game')
        # Add score values to the bars
        for bar in bars:
            width = bar.get_width()
            plt.text(width, bar.get_y() + bar.get_height()/2, 
                    f'{width:.1f}', 
                    ha='left', va='center', 
                    bbox=dict(facecolor='white', alpha=0.8))
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'top_10_games.png'))
        plt.close()
        
        # 4. Score Box Plot
        plt.figure(figsize=(10, 6))
        sns.boxplot(y=[game['Score'] for game in games], color='skyblue')
        plt.title('Distribution of Game Scores', pad=20)
        plt.ylabel('OpenCritic Score')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'score_boxplot.png'))
        plt.close()
        
        logger.info(f"Visualizations saved to {OUTPUT_DIR}")
        
        # Print summary
        print("\nVisualization Summary:")
        print("1. Score Distribution: Shows the spread of game scores")
        print("2. Quality Categories: Shows the proportion of games in each quality category")
        print("3. Top 10 Games: Shows the highest-rated Nintendo Switch games")
        print("4. Score Box Plot: Shows the statistical distribution of scores")
        
    except Exception as e:
        logger.error(f"An error occurred during visualization: {str(e)}")

if __name__ == "__main__":
    create_visualizations() 