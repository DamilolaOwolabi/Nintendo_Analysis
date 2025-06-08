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

def extract_franchise(game_name):
    """Extract franchise name from game name."""
    # Common Nintendo franchises
    franchises = {
        'Mario': ['Mario', 'Super Mario', 'Mario Kart', 'Mario Party', 'Mario Golf', 'Mario Tennis'],
        'Zelda': ['Zelda', 'The Legend of Zelda'],
        'Pokemon': ['Pokemon', 'Pokémon'],
        'Metroid': ['Metroid'],
        'Kirby': ['Kirby'],
        'Donkey Kong': ['Donkey Kong', 'DK'],
        'Animal Crossing': ['Animal Crossing'],
        'Splatoon': ['Splatoon'],
        'Fire Emblem': ['Fire Emblem'],
        'Xenoblade': ['Xenoblade'],
        'Pikmin': ['Pikmin'],
        'Star Fox': ['Star Fox', 'Starfox'],
        'F-Zero': ['F-Zero'],
        'Bayonetta': ['Bayonetta'],
        'Astral Chain': ['Astral Chain'],
        'Arms': ['Arms'],
        'Ring Fit': ['Ring Fit'],
        'Brain Age': ['Brain Age'],
        'Wario': ['Wario'],
        'Yoshi': ['Yoshi']
    }
    
    for franchise, keywords in franchises.items():
        if any(keyword.lower() in game_name.lower() for keyword in keywords):
            return franchise
    return 'Other'

def analyze_franchise_performance():
    logger.info("Analyzing game quality and market performance by franchise")
    
    try:
        # Read the data
        games = []
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    game_name = row['Game']
                    franchise = extract_franchise(game_name)
                    games.append({
                        'Game': game_name,
                        'Franchise': franchise,
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
        
        # 1. Franchise Quality Analysis
        franchise_scores = defaultdict(list)
        for game in games:
            franchise_scores[game['Franchise']].append(game['Score'])
        
        franchise_stats = {
            franchise: {
                'mean': np.mean(scores),
                'median': np.median(scores),
                'count': len(scores)
            }
            for franchise, scores in franchise_scores.items()
        }
        
        # Sort franchises by mean score
        sorted_franchises = sorted(franchise_stats.items(), key=lambda x: x[1]['mean'], reverse=True)
        
        # Create franchise quality bar chart
        plt.figure(figsize=(12, 6))
        franchises = [franchise for franchise, _ in sorted_franchises]
        means = [stats['mean'] for _, stats in sorted_franchises]
        counts = [stats['count'] for _, stats in sorted_franchises]
        
        bars = plt.bar(franchises, means, color='skyblue')
        plt.title('Average Game Quality Score by Franchise', pad=20)
        plt.xlabel('Franchise')
        plt.ylabel('Average Quality Score')
        plt.xticks(rotation=45, ha='right')
        
        # Add count labels on top of bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'n={count}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'franchise_quality.png'))
        plt.close()
        
        # 2. Franchise Distribution Analysis
        franchise_counts = {franchise: len(scores) for franchise, scores in franchise_scores.items()}
        total_games = sum(franchise_counts.values())
        
        # Create franchise distribution pie chart
        plt.figure(figsize=(10, 6))
        plt.pie(franchise_counts.values(),
                labels=franchise_counts.keys(),
                autopct='%1.1f%%',
                colors=sns.color_palette('husl', len(franchise_counts)))
        plt.title('Distribution of Games by Franchise', pad=20)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'franchise_distribution.png'))
        plt.close()
        
        # 3. Franchise Quality Ranges
        quality_ranges = {
            '90-100': (90, 100),
            '80-89': (80, 89),
            '70-79': (70, 79),
            '60-69': (60, 69),
            'Below 60': (0, 59)
        }
        
        franchise_quality_ranges = defaultdict(lambda: {range_name: 0 for range_name in quality_ranges.keys()})
        
        for game in games:
            score = game['Score']
            franchise = game['Franchise']
            for range_name, (min_score, max_score) in quality_ranges.items():
                if min_score <= score <= max_score:
                    franchise_quality_ranges[franchise][range_name] += 1
                    break
        
        # Create stacked bar chart for each franchise
        for franchise in franchises:
            plt.figure(figsize=(10, 6))
            ranges = list(quality_ranges.keys())
            values = [franchise_quality_ranges[franchise][range_name] for range_name in ranges]
            
            bars = plt.bar(ranges, values, color=sns.color_palette('husl', len(ranges)))
            plt.title(f'Quality Score Distribution for {franchise}', pad=20)
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
            plt.savefig(os.path.join(OUTPUT_DIR, f'quality_distribution_{franchise.lower().replace(" ", "_")}.png'))
            plt.close()
        
        # Generate insights
        insights = []
        insights.append("\nFranchise Analysis Insights:")
        insights.append(f"1. Total Games Analyzed: {len(games)}")
        insights.append("\nFranchise Performance:")
        for franchise, stats in sorted_franchises:
            insights.append(f"- {franchise}:")
            insights.append(f"  * Average Score: {stats['mean']:.1f}")
            insights.append(f"  * Median Score: {stats['median']:.1f}")
            insights.append(f"  * Number of Games: {stats['count']}")
        
        # Save insights
        output_file = os.path.join(OUTPUT_DIR, 'franchise_analysis_insights.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(insights))
        
        logger.info(f"Analysis complete. Insights saved to {output_file}")
        
        # Print key insights
        print("\nKey Insights:")
        print(f"1. Total Games Analyzed: {len(games)}")
        print("\nFranchise Performance:")
        for franchise, stats in sorted_franchises:
            print(f"- {franchise}:")
            print(f"  * Average Score: {stats['mean']:.1f}")
            print(f"  * Median Score: {stats['median']:.1f}")
            print(f"  * Number of Games: {stats['count']}")
        
    except Exception as e:
        logger.error(f"An error occurred during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    analyze_franchise_performance() 