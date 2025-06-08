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

def extract_developer(game_name):
    """Extract developer name from game name or metadata."""
    # Common Nintendo developers
    developers = {
        'Nintendo EPD': ['Mario', 'Zelda', 'Animal Crossing', 'Splatoon', 'Arms'],
        'Nintendo EAD': ['Mario', 'Zelda', 'Animal Crossing', 'Splatoon', 'Arms'],
        'Game Freak': ['Pokemon', 'Pokémon'],
        'Retro Studios': ['Metroid', 'Donkey Kong', 'DK'],
        'HAL Laboratory': ['Kirby'],
        'Intelligent Systems': ['Fire Emblem', 'Paper Mario', 'WarioWare'],
        'Monolith Soft': ['Xenoblade'],
        'PlatinumGames': ['Bayonetta', 'Astral Chain'],
        'Nintendo SPD': ['Brain Age', 'Ring Fit'],
        'Nintendo R&D': ['Mario', 'Zelda', 'Animal Crossing'],
        'Nintendo EAD Tokyo': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Kyoto': ['Mario', 'Zelda', 'Animal Crossing'],
        'Nintendo EAD Osaka': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Tokyo 2': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Kyoto 2': ['Mario', 'Zelda', 'Animal Crossing'],
        'Nintendo EAD Osaka 2': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Tokyo 3': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Kyoto 3': ['Mario', 'Zelda', 'Animal Crossing'],
        'Nintendo EAD Osaka 3': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Tokyo 4': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Kyoto 4': ['Mario', 'Zelda', 'Animal Crossing'],
        'Nintendo EAD Osaka 4': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Tokyo 5': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Kyoto 5': ['Mario', 'Zelda', 'Animal Crossing'],
        'Nintendo EAD Osaka 5': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Tokyo 6': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Kyoto 6': ['Mario', 'Zelda', 'Animal Crossing'],
        'Nintendo EAD Osaka 6': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Tokyo 7': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Kyoto 7': ['Mario', 'Zelda', 'Animal Crossing'],
        'Nintendo EAD Osaka 7': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Tokyo 8': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Kyoto 8': ['Mario', 'Zelda', 'Animal Crossing'],
        'Nintendo EAD Osaka 8': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Tokyo 9': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Kyoto 9': ['Mario', 'Zelda', 'Animal Crossing'],
        'Nintendo EAD Osaka 9': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Tokyo 10': ['Mario', 'Donkey Kong', 'DK'],
        'Nintendo EAD Kyoto 10': ['Mario', 'Zelda', 'Animal Crossing'],
        'Nintendo EAD Osaka 10': ['Mario', 'Donkey Kong', 'DK']
    }
    
    for developer, keywords in developers.items():
        if any(keyword.lower() in game_name.lower() for keyword in keywords):
            return developer
    return 'Other'

def analyze_developer_performance():
    logger.info("Analyzing game quality and market performance by developer")
    
    try:
        # Read the data
        games = []
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    game_name = row['Game']
                    developer = extract_developer(game_name)
                    games.append({
                        'Game': game_name,
                        'Developer': developer,
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
        
        # 1. Developer Quality Analysis
        developer_scores = defaultdict(list)
        for game in games:
            developer_scores[game['Developer']].append(game['Score'])
        
        developer_stats = {
            developer: {
                'mean': np.mean(scores),
                'median': np.median(scores),
                'count': len(scores)
            }
            for developer, scores in developer_scores.items()
        }
        
        # Sort developers by mean score
        sorted_developers = sorted(developer_stats.items(), key=lambda x: x[1]['mean'], reverse=True)
        
        # Create developer quality bar chart
        plt.figure(figsize=(12, 6))
        developers = [developer for developer, _ in sorted_developers]
        means = [stats['mean'] for _, stats in sorted_developers]
        counts = [stats['count'] for _, stats in sorted_developers]
        
        bars = plt.bar(developers, means, color='skyblue')
        plt.title('Average Game Quality Score by Developer', pad=20)
        plt.xlabel('Developer')
        plt.ylabel('Average Quality Score')
        plt.xticks(rotation=45, ha='right')
        
        # Add count labels on top of bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'n={count}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'developer_quality.png'))
        plt.close()
        
        # 2. Developer Distribution Analysis
        developer_counts = {developer: len(scores) for developer, scores in developer_scores.items()}
        total_games = sum(developer_counts.values())
        
        # Create developer distribution pie chart
        plt.figure(figsize=(10, 6))
        plt.pie(developer_counts.values(),
                labels=developer_counts.keys(),
                autopct='%1.1f%%',
                colors=sns.color_palette('husl', len(developer_counts)))
        plt.title('Distribution of Games by Developer', pad=20)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'developer_distribution.png'))
        plt.close()
        
        # 3. Developer Quality Ranges
        quality_ranges = {
            '90-100': (90, 100),
            '80-89': (80, 89),
            '70-79': (70, 79),
            '60-69': (60, 69),
            'Below 60': (0, 59)
        }
        
        developer_quality_ranges = defaultdict(lambda: {range_name: 0 for range_name in quality_ranges.keys()})
        
        for game in games:
            score = game['Score']
            developer = game['Developer']
            for range_name, (min_score, max_score) in quality_ranges.items():
                if min_score <= score <= max_score:
                    developer_quality_ranges[developer][range_name] += 1
                    break
        
        # Create stacked bar chart for each developer
        for developer in developers:
            plt.figure(figsize=(10, 6))
            ranges = list(quality_ranges.keys())
            values = [developer_quality_ranges[developer][range_name] for range_name in ranges]
            
            bars = plt.bar(ranges, values, color=sns.color_palette('husl', len(ranges)))
            plt.title(f'Quality Score Distribution for {developer}', pad=20)
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
            plt.savefig(os.path.join(OUTPUT_DIR, f'quality_distribution_{developer.lower().replace(" ", "_")}.png'))
            plt.close()
        
        # Generate insights
        insights = []
        insights.append("\nDeveloper Analysis Insights:")
        insights.append(f"1. Total Games Analyzed: {len(games)}")
        insights.append("\nDeveloper Performance:")
        for developer, stats in sorted_developers:
            insights.append(f"- {developer}:")
            insights.append(f"  * Average Score: {stats['mean']:.1f}")
            insights.append(f"  * Median Score: {stats['median']:.1f}")
            insights.append(f"  * Number of Games: {stats['count']}")
        
        # Save insights
        output_file = os.path.join(OUTPUT_DIR, 'developer_analysis_insights.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(insights))
        
        logger.info(f"Analysis complete. Insights saved to {output_file}")
        
        # Print key insights
        print("\nKey Insights:")
        print(f"1. Total Games Analyzed: {len(games)}")
        print("\nDeveloper Performance:")
        for developer, stats in sorted_developers:
            print(f"- {developer}:")
            print(f"  * Average Score: {stats['mean']:.1f}")
            print(f"  * Median Score: {stats['median']:.1f}")
            print(f"  * Number of Games: {stats['count']}")
        
    except Exception as e:
        logger.error(f"An error occurred during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    analyze_developer_performance() 