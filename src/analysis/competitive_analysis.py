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

def analyze_competitive_landscape():
    logger.info("Analyzing competitive landscape and pricing strategies")
    
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
        
        # 1. Quality vs Price Analysis
        quality_ranges = {
            '90-100': (90, 100),
            '80-89': (80, 89),
            '70-79': (70, 79),
            '60-69': (60, 69),
            'Below 60': (0, 59)
        }
        
        quality_counts = {range_name: 0 for range_name in quality_ranges.keys()}
        for game in games:
            score = game['Score']
            for range_name, (min_score, max_score) in quality_ranges.items():
                if min_score <= score <= max_score:
                    quality_counts[range_name] += 1
                    break
        
        # Create quality distribution plot
        plt.figure(figsize=(12, 6))
        bars = plt.bar(quality_counts.keys(), quality_counts.values(), color='skyblue')
        plt.title('Distribution of Games by Quality Score', pad=20)
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
        plt.savefig(os.path.join(OUTPUT_DIR, 'quality_distribution.png'))
        plt.close()
        
        # 2. Competitive Analysis
        # Define market segments based on quality
        market_segments = {
            'Premium (90-100)': 0,
            'High-End (80-89)': 0,
            'Mid-Range (70-79)': 0,
            'Budget (60-69)': 0,
            'Value (<60)': 0
        }
        
        for game in games:
            score = game['Score']
            if score >= 90:
                market_segments['Premium (90-100)'] += 1
            elif score >= 80:
                market_segments['High-End (80-89)'] += 1
            elif score >= 70:
                market_segments['Mid-Range (70-79)'] += 1
            elif score >= 60:
                market_segments['Budget (60-69)'] += 1
            else:
                market_segments['Value (<60)'] += 1
        
        # Create market segments pie chart
        plt.figure(figsize=(10, 6))
        plt.pie(market_segments.values(),
                labels=market_segments.keys(),
                autopct='%1.1f%%',
                colors=['#2ecc71', '#27ae60', '#f1c40f', '#e67e22', '#e74c3c'])
        plt.title('Distribution of Games by Market Segment', pad=20)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'market_segments.png'))
        plt.close()
        
        # 3. Competitive Positioning Analysis
        positioning = {
            'Market Leader': 0,
            'Strong Competitor': 0,
            'Niche Player': 0
        }
        
        for game in games:
            score = game['Score']
            if score >= 85:
                positioning['Market Leader'] += 1
            elif score >= 75:
                positioning['Strong Competitor'] += 1
            else:
                positioning['Niche Player'] += 1
        
        # Create positioning bar chart
        plt.figure(figsize=(10, 6))
        bars = plt.bar(positioning.keys(), positioning.values(), color='skyblue')
        plt.title('Competitive Positioning by Game Quality', pad=20)
        plt.xlabel('Market Position')
        plt.ylabel('Number of Games')
        
        # Add count labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'competitive_positioning.png'))
        plt.close()
        
        # Generate insights
        insights = []
        insights.append("\nCompetitive Analysis Insights:")
        insights.append(f"1. Total Games Analyzed: {len(games)}")
        insights.append("\nMarket Segments:")
        for segment, count in market_segments.items():
            percentage = (count / len(games)) * 100
            insights.append(f"- {segment}: {count} games ({percentage:.1f}%)")
        
        insights.append("\nCompetitive Positioning:")
        for position, count in positioning.items():
            percentage = (count / len(games)) * 100
            insights.append(f"- {position}: {count} games ({percentage:.1f}%)")
        
        # Save insights
        output_file = os.path.join(OUTPUT_DIR, 'competitive_analysis_insights.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(insights))
        
        logger.info(f"Analysis complete. Insights saved to {output_file}")
        
        # Print key insights
        print("\nKey Insights:")
        print(f"1. Total Games Analyzed: {len(games)}")
        print("\nMarket Segments:")
        for segment, count in market_segments.items():
            percentage = (count / len(games)) * 100
            print(f"- {segment}: {count} games ({percentage:.1f}%)")
        
        print("\nCompetitive Positioning:")
        for position, count in positioning.items():
            percentage = (count / len(games)) * 100
            print(f"- {position}: {count} games ({percentage:.1f}%)")
        
    except Exception as e:
        logger.error(f"An error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    analyze_competitive_landscape() 