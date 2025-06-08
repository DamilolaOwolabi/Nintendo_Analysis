import csv
import os
import logging
from datetime import datetime
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw', 'nintendo_game_scores.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'processed')

def analyze_game_quality():
    logger.info("Analyzing game quality data")
    
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
        
        # Calculate basic statistics
        total_games = len(games)
        avg_score = sum(game['Score'] for game in games) / total_games
        high_quality_games = sum(1 for game in games if game['Score'] >= 80)
        medium_quality_games = sum(1 for game in games if 60 <= game['Score'] < 80)
        low_quality_games = sum(1 for game in games if game['Score'] < 60)
        
        # Analyze by year
        games_by_year = defaultdict(list)
        for game in games:
            if game['Release Date']:
                try:
                    year = datetime.strptime(game['Release Date'], '%Y-%m-%d').year
                    games_by_year[year].append(game)
                except:
                    continue
        
        # Calculate yearly statistics
        yearly_stats = {}
        for year, year_games in games_by_year.items():
            if year_games:
                yearly_stats[year] = {
                    'count': len(year_games),
                    'avg_score': sum(game['Score'] for game in year_games) / len(year_games),
                    'high_quality': sum(1 for game in year_games if game['Score'] >= 80),
                    'medium_quality': sum(1 for game in year_games if 60 <= game['Score'] < 80),
                    'low_quality': sum(1 for game in year_games if game['Score'] < 60)
                }
        
        # Generate insights
        insights = []
        
        # Overall quality insights
        insights.append(f"Total Nintendo Switch games analyzed: {total_games}")
        insights.append(f"Average game score: {avg_score:.1f}")
        insights.append(f"High quality games (score >= 80): {high_quality_games} ({high_quality_games/total_games*100:.1f}%)")
        insights.append(f"Medium quality games (score 60-79): {medium_quality_games} ({medium_quality_games/total_games*100:.1f}%)")
        insights.append(f"Low quality games (score < 60): {low_quality_games} ({low_quality_games/total_games*100:.1f}%)")
        
        # Yearly trends
        insights.append("\nYearly Trends:")
        for year in sorted(yearly_stats.keys()):
            stats = yearly_stats[year]
            insights.append(f"\n{year}:")
            insights.append(f"  Games released: {stats['count']}")
            insights.append(f"  Average score: {stats['avg_score']:.1f}")
            insights.append(f"  High quality games: {stats['high_quality']} ({stats['high_quality']/stats['count']*100:.1f}%)")
            insights.append(f"  Medium quality games: {stats['medium_quality']} ({stats['medium_quality']/stats['count']*100:.1f}%)")
            insights.append(f"  Low quality games: {stats['low_quality']} ({stats['low_quality']/stats['count']*100:.1f}%)")
        
        # Top 10 games
        top_games = sorted(games, key=lambda x: x['Score'], reverse=True)[:10]
        insights.append("\nTop 10 Games by Score:")
        for i, game in enumerate(top_games, 1):
            insights.append(f"{i}. {game['Game']} - Score: {game['Score']:.1f} (Released: {game['Release Date']})")
        
        # Save insights
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, 'game_quality_insights.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(insights))
        
        logger.info(f"Analysis complete. Insights saved to {output_file}")
        
        # Print key insights for immediate review
        print("\nKey Insights:")
        print(f"1. {high_quality_games/total_games*100:.1f}% of Nintendo Switch games are high quality (score >= 80)")
        print(f"2. Average game score: {avg_score:.1f}")
        print(f"3. Only {low_quality_games/total_games*100:.1f}% of games are low quality (score < 60)")
        
    except Exception as e:
        logger.error(f"An error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    analyze_game_quality() 