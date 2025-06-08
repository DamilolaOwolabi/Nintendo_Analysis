import csv
import os
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw', 'nintendo_game_scores.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'processed', 'visualizations')

def analyze_quality_sales_relationship():
    logger.info("Analyzing relationship between game quality and sales performance")
    
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
        
        # 1. Quality Score Distribution
        scores = [game['Score'] for game in games]
        
        plt.figure(figsize=(12, 6))
        sns.histplot(scores, bins=20, color='skyblue', edgecolor='black')
        plt.title('Distribution of Game Quality Scores', pad=20)
        plt.xlabel('OpenCritic Score')
        plt.ylabel('Number of Games')
        plt.axvline(np.mean(scores), color='red', linestyle='--', label=f'Mean: {np.mean(scores):.1f}')
        plt.axvline(np.median(scores), color='green', linestyle='--', label=f'Median: {np.median(scores):.1f}')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'quality_score_distribution.png'))
        plt.close()
        
        # 2. Quality Categories Analysis
        quality_categories = {
            'Exceptional (90-100)': 0,
            'Excellent (80-89)': 0,
            'Good (70-79)': 0,
            'Average (60-69)': 0,
            'Below Average (<60)': 0
        }
        
        for game in games:
            score = game['Score']
            if score >= 90:
                quality_categories['Exceptional (90-100)'] += 1
            elif score >= 80:
                quality_categories['Excellent (80-89)'] += 1
            elif score >= 70:
                quality_categories['Good (70-79)'] += 1
            elif score >= 60:
                quality_categories['Average (60-69)'] += 1
            else:
                quality_categories['Below Average (<60)'] += 1
        
        # Create quality categories pie chart
        plt.figure(figsize=(10, 6))
        plt.pie(quality_categories.values(),
                labels=quality_categories.keys(),
                autopct='%1.1f%%',
                colors=['#2ecc71', '#27ae60', '#f1c40f', '#e67e22', '#e74c3c'])
        plt.title('Distribution of Games by Quality Category', pad=20)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'quality_categories.png'))
        plt.close()
        
        # 3. Quality vs Market Success Analysis
        quality_ranges = {
            '90-100': (90, 100),
            '80-89': (80, 89),
            '70-79': (70, 79),
            '60-69': (60, 69),
            'Below 60': (0, 59)
        }
        
        market_success = {range_name: 0 for range_name in quality_ranges.keys()}
        for game in games:
            score = game['Score']
            for range_name, (min_score, max_score) in quality_ranges.items():
                if min_score <= score <= max_score:
                    market_success[range_name] += 1
                    break
        
        # Create market success bar chart
        plt.figure(figsize=(12, 6))
        bars = plt.bar(market_success.keys(), market_success.values(), color='skyblue')
        plt.title('Market Success by Quality Range', pad=20)
        plt.xlabel('Quality Score Range')
        plt.ylabel('Number of Games')
        plt.xticks(rotation=45)
        
        # Add count labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'market_success_by_quality.png'))
        plt.close()
        
        # Generate insights
        insights = []
        insights.append("\nQuality and Market Success Analysis:")
        insights.append(f"1. Average Quality Score: {np.mean(scores):.1f}")
        insights.append(f"2. Median Quality Score: {np.median(scores):.1f}")
        insights.append("\nQuality Categories Distribution:")
        for category, count in quality_categories.items():
            percentage = (count / len(games)) * 100
            insights.append(f"- {category}: {count} games ({percentage:.1f}%)")
        
        # Save insights
        output_file = os.path.join(OUTPUT_DIR, 'quality_sales_insights.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(insights))
        
        logger.info(f"Analysis complete. Insights saved to {output_file}")
        
        # Print key insights
        print("\nKey Insights:")
        print(f"1. Average Quality Score: {np.mean(scores):.1f}")
        print(f"2. Median Quality Score: {np.median(scores):.1f}")
        print("\nQuality Categories:")
        for category, count in quality_categories.items():
            percentage = (count / len(games)) * 100
            print(f"- {category}: {count} games ({percentage:.1f}%)")
        
    except Exception as e:
        logger.error(f"An error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    analyze_quality_sales_relationship() 