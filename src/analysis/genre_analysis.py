import csv
import os
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw', 'nintendo_game_scores.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'processed', 'visualizations')

def extract_genre(game_name):
    """Extract genre from game name."""
    # Common game genres
    genres = {
        'Action': ['Action', 'Fighting', 'Beat \'em up', 'Hack and slash'],
        'Adventure': ['Adventure', 'Action-Adventure', 'Action Adventure'],
        'RPG': ['RPG', 'Role-Playing', 'Role Playing', 'JRPG', 'SRPG', 'Tactical RPG'],
        'Platformer': ['Platformer', 'Platform', '2D Platformer', '3D Platformer'],
        'Racing': ['Racing', 'Kart Racing', 'Racing Game'],
        'Sports': ['Sports', 'Tennis', 'Golf', 'Baseball', 'Soccer', 'Football', 'Basketball'],
        'Puzzle': ['Puzzle', 'Brain Training', 'Educational'],
        'Strategy': ['Strategy', 'Tactics', 'Tactical', 'Real-time Strategy', 'Turn-based Strategy'],
        'Simulation': ['Simulation', 'Life Simulation', 'Social Simulation', 'Farming Simulation'],
        'Party': ['Party', 'Mini-games', 'Mini games', 'Party Game'],
        'Fighting': ['Fighting', 'Fighter', 'Versus Fighting'],
        'Shooter': ['Shooter', 'First-person Shooter', 'Third-person Shooter', 'FPS', 'TPS'],
        'Stealth': ['Stealth', 'Sneak', 'Infiltration'],
        'Survival': ['Survival', 'Survival Horror', 'Horror'],
        'Rhythm': ['Rhythm', 'Music', 'Dance', 'Dancing'],
        'Educational': ['Educational', 'Learning', 'Training', 'Brain Training'],
        'Fitness': ['Fitness', 'Exercise', 'Workout', 'Health'],
        'Social': ['Social', 'Communication', 'Chat', 'Messaging'],
        'Utility': ['Utility', 'Tool', 'Application', 'App'],
        'Other': ['Other', 'Miscellaneous', 'Misc']
    }
    
    for genre, keywords in genres.items():
        if any(keyword.lower() in game_name.lower() for keyword in keywords):
            return genre
    return 'Other'

def analyze_genre_performance():
    logger.info("Analyzing game quality and market performance by genre")
    
    try:
        # Read the data
        games = []
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    game_name = row['Game']
                    genre = extract_genre(game_name)
                    games.append({
                        'Game': game_name,
                        'Genre': genre,
                        'Score': float(row['OpenCritic Score']),
                        'Release Date': row['Release Date']
                    })
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error processing game {row.get('Game', 'Unknown')}: {str(e)}")
                    continue
        
        if not games:
            logger.error("No valid game data found")
            return
        
        logger.info(f"Successfully processed {len(games)} games")
        
        # Create output directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Set style
        plt.style.use('default')
        sns.set_theme()
        
        # 1. Genre Quality Analysis
        genre_scores = defaultdict(list)
        for game in games:
            genre_scores[game['Genre']].append(game['Score'])
        
        genre_stats = {
            genre: {
                'mean': np.mean(scores),
                'median': np.median(scores),
                'count': len(scores)
            }
            for genre, scores in genre_scores.items()
        }
        
        # Sort genres by mean score
        sorted_genres = sorted(genre_stats.items(), key=lambda x: x[1]['mean'], reverse=True)
        
        # Create genre quality bar chart
        plt.figure(figsize=(12, 6))
        genres = [genre for genre, _ in sorted_genres]
        means = [stats['mean'] for _, stats in sorted_genres]
        counts = [stats['count'] for _, stats in sorted_genres]
        
        bars = plt.bar(genres, means, color='skyblue')
        plt.title('Average Game Quality Score by Genre', pad=20)
        plt.xlabel('Genre')
        plt.ylabel('Average Quality Score')
        plt.xticks(rotation=45, ha='right')
        
        # Add count labels on top of bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'n={count}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'genre_quality.png'))
        plt.close()
        
        # 2. Genre Distribution Analysis
        genre_counts = {genre: len(scores) for genre, scores in genre_scores.items()}
        total_games = sum(genre_counts.values())
        
        # Create genre distribution pie chart
        plt.figure(figsize=(10, 6))
        plt.pie(genre_counts.values(),
                labels=genre_counts.keys(),
                autopct='%1.1f%%',
                colors=sns.color_palette('husl', len(genre_counts)))
        plt.title('Distribution of Games by Genre', pad=20)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'genre_distribution.png'))
        plt.close()
        
        # 3. Genre Quality Ranges
        quality_ranges = {
            '90-100': (90, 100),
            '80-89': (80, 89),
            '70-79': (70, 79),
            '60-69': (60, 69),
            'Below 60': (0, 59)
        }
        
        genre_quality_ranges = defaultdict(lambda: {range_name: 0 for range_name in quality_ranges.keys()})
        
        for game in games:
            score = game['Score']
            genre = game['Genre']
            for range_name, (min_score, max_score) in quality_ranges.items():
                if min_score <= score <= max_score:
                    genre_quality_ranges[genre][range_name] += 1
                    break
        
        # Create stacked bar chart for each genre
        for genre in genres:
            plt.figure(figsize=(10, 6))
            ranges = list(quality_ranges.keys())
            values = [genre_quality_ranges[genre][range_name] for range_name in ranges]
            
            bars = plt.bar(ranges, values, color=sns.color_palette('husl', len(ranges)))
            plt.title(f'Quality Score Distribution for {genre}', pad=20)
            plt.xlabel('Quality Score Range')
            plt.ylabel('Number of Games')
            plt.xticks(rotation=45)
            
            # Add count labels on top of bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    plt.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}',
                            ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(os.path.join(OUTPUT_DIR, f'quality_distribution_{genre.lower().replace(" ", "_")}.png'))
            plt.close()
        
        # Generate insights
        insights = []
        insights.append("\nGenre Analysis Insights:")
        insights.append(f"1. Total Games Analyzed: {len(games)}")
        insights.append("\nGenre Performance:")
        for genre, stats in sorted_genres:
            insights.append(f"- {genre}:")
            insights.append(f"  * Average Score: {stats['mean']:.1f}")
            insights.append(f"  * Median Score: {stats['median']:.1f}")
            insights.append(f"  * Number of Games: {stats['count']}")
        
        # Save insights
        output_file = os.path.join(OUTPUT_DIR, 'genre_analysis_insights.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(insights))
        
        logger.info(f"Analysis complete. Insights saved to {output_file}")
        
        # Print key insights
        print("\nKey Insights:")
        print(f"1. Total Games Analyzed: {len(games)}")
        print("\nGenre Performance:")
        for genre, stats in sorted_genres:
            print(f"- {genre}:")
            print(f"  * Average Score: {stats['mean']:.1f}")
            print(f"  * Median Score: {stats['median']:.1f}")
            print(f"  * Number of Games: {stats['count']}")
        
    except Exception as e:
        logger.error(f"An error occurred during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    analyze_genre_performance() 