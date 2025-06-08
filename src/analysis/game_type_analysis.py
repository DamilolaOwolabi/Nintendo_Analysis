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

def extract_game_type(game_name):
    """Extract game type from game name."""
    # Common game types
    game_types = {
        'Main Series': ['Mario', 'Zelda', 'Pokemon', 'Metroid', 'Kirby', 'Fire Emblem', 'Animal Crossing', 'Splatoon', 'Donkey Kong', 'Xenoblade', 'Bayonetta', 'Pikmin', 'Star Fox', 'F-Zero', 'Wario', 'Yoshi', 'Luigi'],
        'Spin-off': ['Mario Kart', 'Mario Party', 'Mario Golf', 'Mario Tennis', 'Mario Strikers', 'Mario + Rabbids', 'Mario & Sonic', 'Mario & Luigi', 'Mario vs. Donkey Kong', 'Mario Sports', 'Paper Mario', 'WarioWare'],
        'Remake': ['Remake', 'Remaster', 'HD', 'Deluxe', 'Definitive Edition', 'Anniversary', 'Collection'],
        'Port': ['Port', 'Switch', 'Nintendo Switch'],
        'DLC': ['DLC', 'Expansion', 'Pass', 'Pack'],
        'Indie': ['Indie', 'Independent'],
        'Third Party': ['Third Party', 'Third-Party'],
        'First Party': ['First Party', 'First-Party'],
        'Second Party': ['Second Party', 'Second-Party'],
        'Exclusive': ['Exclusive', 'Nintendo Exclusive'],
        'Multiplatform': ['Multiplatform', 'Multi-Platform'],
        'Digital Only': ['Digital Only', 'Digital-Only'],
        'Physical Only': ['Physical Only', 'Physical-Only'],
        'Free to Play': ['Free to Play', 'Free-to-Play', 'F2P'],
        'Premium': ['Premium', 'Full Price'],
        'Budget': ['Budget', 'Budget Price'],
        'Mid-Range': ['Mid-Range', 'Mid-Range Price'],
        'High-End': ['High-End', 'High-End Price'],
        'Ultra': ['Ultra', 'Ultra Price'],
        'Luxury': ['Luxury', 'Luxury Price']
    }
    
    for game_type, keywords in game_types.items():
        if any(keyword.lower() in game_name.lower() for keyword in keywords):
            return game_type
    return 'Other'

def analyze_game_type_performance():
    logger.info("Analyzing game quality and market performance by game type")
    
    try:
        # Read the data
        games = []
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    game_name = row['Game']
                    game_type = extract_game_type(game_name)
                    games.append({
                        'Game': game_name,
                        'Game Type': game_type,
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
        
        # 1. Game Type Quality Analysis
        game_type_scores = defaultdict(list)
        for game in games:
            game_type_scores[game['Game Type']].append(game['Score'])
        
        game_type_stats = {
            game_type: {
                'mean': np.mean(scores),
                'median': np.median(scores),
                'count': len(scores)
            }
            for game_type, scores in game_type_scores.items()
        }
        
        # Sort game types by mean score
        sorted_game_types = sorted(game_type_stats.items(), key=lambda x: x[1]['mean'], reverse=True)
        
        # Create game type quality bar chart
        plt.figure(figsize=(12, 6))
        game_types = [game_type for game_type, _ in sorted_game_types]
        means = [stats['mean'] for _, stats in sorted_game_types]
        counts = [stats['count'] for _, stats in sorted_game_types]
        
        bars = plt.bar(game_types, means, color='skyblue')
        plt.title('Average Game Quality Score by Game Type', pad=20)
        plt.xlabel('Game Type')
        plt.ylabel('Average Quality Score')
        plt.xticks(rotation=45, ha='right')
        
        # Add count labels on top of bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'n={count}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'game_type_quality.png'))
        plt.close()
        
        # 2. Game Type Distribution Analysis
        game_type_counts = {game_type: len(scores) for game_type, scores in game_type_scores.items()}
        total_games = sum(game_type_counts.values())
        
        # Create game type distribution pie chart
        plt.figure(figsize=(10, 6))
        plt.pie(game_type_counts.values(),
                labels=game_type_counts.keys(),
                autopct='%1.1f%%',
                colors=sns.color_palette('husl', len(game_type_counts)))
        plt.title('Distribution of Games by Game Type', pad=20)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'game_type_distribution.png'))
        plt.close()
        
        # 3. Game Type Quality Ranges
        quality_ranges = {
            '90-100': (90, 100),
            '80-89': (80, 89),
            '70-79': (70, 79),
            '60-69': (60, 69),
            'Below 60': (0, 59)
        }
        
        game_type_quality_ranges = defaultdict(lambda: {range_name: 0 for range_name in quality_ranges.keys()})
        
        for game in games:
            score = game['Score']
            game_type = game['Game Type']
            for range_name, (min_score, max_score) in quality_ranges.items():
                if min_score <= score <= max_score:
                    game_type_quality_ranges[game_type][range_name] += 1
                    break
        
        # Create stacked bar chart for each game type
        for game_type in game_types:
            plt.figure(figsize=(10, 6))
            ranges = list(quality_ranges.keys())
            values = [game_type_quality_ranges[game_type][range_name] for range_name in ranges]
            
            bars = plt.bar(ranges, values, color=sns.color_palette('husl', len(ranges)))
            plt.title(f'Quality Score Distribution for {game_type}', pad=20)
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
            plt.savefig(os.path.join(OUTPUT_DIR, f'quality_distribution_{game_type.lower().replace(" ", "_")}.png'))
            plt.close()
        
        # Generate insights
        insights = []
        insights.append("\nGame Type Analysis Insights:")
        insights.append(f"1. Total Games Analyzed: {len(games)}")
        insights.append("\nGame Type Performance:")
        for game_type, stats in sorted_game_types:
            insights.append(f"- {game_type}:")
            insights.append(f"  * Average Score: {stats['mean']:.1f}")
            insights.append(f"  * Median Score: {stats['median']:.1f}")
            insights.append(f"  * Number of Games: {stats['count']}")
        
        # Save insights
        output_file = os.path.join(OUTPUT_DIR, 'game_type_analysis_insights.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(insights))
        
        logger.info(f"Analysis complete. Insights saved to {output_file}")
        
        # Print key insights
        print("\nKey Insights:")
        print(f"1. Total Games Analyzed: {len(games)}")
        print("\nGame Type Performance:")
        for game_type, stats in sorted_game_types:
            print(f"- {game_type}:")
            print(f"  * Average Score: {stats['mean']:.1f}")
            print(f"  * Median Score: {stats['median']:.1f}")
            print(f"  * Number of Games: {stats['count']}")
        
    except Exception as e:
        logger.error(f"An error occurred during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    analyze_game_type_performance() 