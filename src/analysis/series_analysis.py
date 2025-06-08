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

def extract_series(game_name):
    """Extract series name from game name."""
    # Common Nintendo series
    series = {
        'Mario': ['Mario', 'Super Mario', 'Mario Kart', 'Mario Party', 'Mario Golf', 'Mario Tennis', 'Mario Strikers', 'Mario + Rabbids'],
        'Zelda': ['Zelda', 'The Legend of Zelda', 'Hyrule'],
        'Pokemon': ['Pokemon', 'Pokémon'],
        'Metroid': ['Metroid'],
        'Kirby': ['Kirby'],
        'Fire Emblem': ['Fire Emblem'],
        'Animal Crossing': ['Animal Crossing'],
        'Splatoon': ['Splatoon'],
        'Donkey Kong': ['Donkey Kong', 'DK'],
        'Xenoblade': ['Xenoblade'],
        'Bayonetta': ['Bayonetta'],
        'Pikmin': ['Pikmin'],
        'Star Fox': ['Star Fox', 'StarFox'],
        'F-Zero': ['F-Zero'],
        'Wario': ['Wario', 'WarioWare'],
        'Yoshi': ['Yoshi'],
        'Luigi': ['Luigi'],
        'Paper Mario': ['Paper Mario'],
        'Mario & Luigi': ['Mario & Luigi'],
        'Mario vs. Donkey Kong': ['Mario vs. Donkey Kong'],
        'Mario Sports': ['Mario Sports'],
        'Mario Party': ['Mario Party'],
        'Mario Kart': ['Mario Kart'],
        'Mario Golf': ['Mario Golf'],
        'Mario Tennis': ['Mario Tennis'],
        'Mario Strikers': ['Mario Strikers'],
        'Mario + Rabbids': ['Mario + Rabbids'],
        'Mario & Sonic': ['Mario & Sonic'],
        'Mario & Luigi': ['Mario & Luigi'],
        'Mario vs. Donkey Kong': ['Mario vs. Donkey Kong'],
        'Mario Sports': ['Mario Sports'],
        'Mario Party': ['Mario Party'],
        'Mario Kart': ['Mario Kart'],
        'Mario Golf': ['Mario Golf'],
        'Mario Tennis': ['Mario Tennis'],
        'Mario Strikers': ['Mario Strikers'],
        'Mario + Rabbids': ['Mario + Rabbids'],
        'Mario & Sonic': ['Mario & Sonic']
    }
    
    for series_name, keywords in series.items():
        if any(keyword.lower() in game_name.lower() for keyword in keywords):
            return series_name
    return 'Other'

def analyze_series_performance():
    logger.info("Analyzing game quality and market performance by series")
    
    try:
        # Read the data
        games = []
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    game_name = row['Game']
                    series = extract_series(game_name)
                    games.append({
                        'Game': game_name,
                        'Series': series,
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
        
        # 1. Series Quality Analysis
        series_scores = defaultdict(list)
        for game in games:
            series_scores[game['Series']].append(game['Score'])
        
        series_stats = {
            series: {
                'mean': np.mean(scores),
                'median': np.median(scores),
                'count': len(scores)
            }
            for series, scores in series_scores.items()
        }
        
        # Sort series by mean score
        sorted_series = sorted(series_stats.items(), key=lambda x: x[1]['mean'], reverse=True)
        
        # Create series quality bar chart
        plt.figure(figsize=(12, 6))
        series_names = [series for series, _ in sorted_series]
        means = [stats['mean'] for _, stats in sorted_series]
        counts = [stats['count'] for _, stats in sorted_series]
        
        bars = plt.bar(series_names, means, color='skyblue')
        plt.title('Average Game Quality Score by Series', pad=20)
        plt.xlabel('Series')
        plt.ylabel('Average Quality Score')
        plt.xticks(rotation=45, ha='right')
        
        # Add count labels on top of bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'n={count}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'series_quality.png'))
        plt.close()
        
        # 2. Series Distribution Analysis
        series_counts = {series: len(scores) for series, scores in series_scores.items()}
        total_games = sum(series_counts.values())
        
        # Create series distribution pie chart
        plt.figure(figsize=(10, 6))
        plt.pie(series_counts.values(),
                labels=series_counts.keys(),
                autopct='%1.1f%%',
                colors=sns.color_palette('husl', len(series_counts)))
        plt.title('Distribution of Games by Series', pad=20)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'series_distribution.png'))
        plt.close()
        
        # 3. Series Quality Ranges
        quality_ranges = {
            '90-100': (90, 100),
            '80-89': (80, 89),
            '70-79': (70, 79),
            '60-69': (60, 69),
            'Below 60': (0, 59)
        }
        
        series_quality_ranges = defaultdict(lambda: {range_name: 0 for range_name in quality_ranges.keys()})
        
        for game in games:
            score = game['Score']
            series = game['Series']
            for range_name, (min_score, max_score) in quality_ranges.items():
                if min_score <= score <= max_score:
                    series_quality_ranges[series][range_name] += 1
                    break
        
        # Create stacked bar chart for each series
        for series in series_names:
            plt.figure(figsize=(10, 6))
            ranges = list(quality_ranges.keys())
            values = [series_quality_ranges[series][range_name] for range_name in ranges]
            
            bars = plt.bar(ranges, values, color=sns.color_palette('husl', len(ranges)))
            plt.title(f'Quality Score Distribution for {series}', pad=20)
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
            plt.savefig(os.path.join(OUTPUT_DIR, f'quality_distribution_{series.lower().replace(" ", "_")}.png'))
            plt.close()
        
        # Generate insights
        insights = []
        insights.append("\nSeries Analysis Insights:")
        insights.append(f"1. Total Games Analyzed: {len(games)}")
        insights.append("\nSeries Performance:")
        for series, stats in sorted_series:
            insights.append(f"- {series}:")
            insights.append(f"  * Average Score: {stats['mean']:.1f}")
            insights.append(f"  * Median Score: {stats['median']:.1f}")
            insights.append(f"  * Number of Games: {stats['count']}")
        
        # Save insights
        output_file = os.path.join(OUTPUT_DIR, 'series_analysis_insights.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(insights))
        
        logger.info(f"Analysis complete. Insights saved to {output_file}")
        
        # Print key insights
        print("\nKey Insights:")
        print(f"1. Total Games Analyzed: {len(games)}")
        print("\nSeries Performance:")
        for series, stats in sorted_series:
            print(f"- {series}:")
            print(f"  * Average Score: {stats['mean']:.1f}")
            print(f"  * Median Score: {stats['median']:.1f}")
            print(f"  * Number of Games: {stats['count']}")
        
    except Exception as e:
        logger.error(f"An error occurred during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    analyze_series_performance() 