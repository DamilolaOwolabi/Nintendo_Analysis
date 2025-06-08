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

def parse_date(date_str):
    """Parse date string into datetime object."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%Y')
            except ValueError:
                logger.warning(f"Could not parse date: {date_str}")
                return None

def analyze_temporal_trends():
    logger.info("Analyzing temporal trends in game quality and market performance")
    
    try:
        # Read the data
        games = []
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    release_date = parse_date(row['Release Date'])
                    if release_date:
                        games.append({
                            'Game': row['Game'],
                            'Score': float(row['OpenCritic Score']),
                            'Release Date': release_date,
                            'Year': release_date.year,
                            'Month': release_date.month,
                            'Quarter': (release_date.month - 1) // 3 + 1
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
        
        # 1. Yearly Quality Trends
        yearly_scores = defaultdict(list)
        for game in games:
            yearly_scores[game['Year']].append(game['Score'])
        
        yearly_stats = {
            year: {
                'mean': np.mean(scores),
                'median': np.median(scores),
                'count': len(scores)
            }
            for year, scores in yearly_scores.items()
        }
        
        # Sort years
        sorted_years = sorted(yearly_stats.items())
        years = [year for year, _ in sorted_years]
        means = [stats['mean'] for _, stats in sorted_years]
        counts = [stats['count'] for _, stats in sorted_years]
        
        # Create yearly quality trend line
        plt.figure(figsize=(12, 6))
        plt.plot(years, means, marker='o', linestyle='-', color='skyblue')
        plt.title('Average Game Quality Score by Year', pad=20)
        plt.xlabel('Year')
        plt.ylabel('Average Quality Score')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add count labels
        for i, count in enumerate(counts):
            plt.text(years[i], means[i], f'n={count}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'yearly_quality_trend.png'))
        plt.close()
        
        # 2. Quarterly Quality Trends
        quarterly_scores = defaultdict(list)
        for game in games:
            quarter = f"{game['Year']} Q{game['Quarter']}"
            quarterly_scores[quarter].append(game['Score'])
        
        quarterly_stats = {
            quarter: {
                'mean': np.mean(scores),
                'median': np.median(scores),
                'count': len(scores)
            }
            for quarter, scores in quarterly_scores.items()
        }
        
        # Sort quarters
        sorted_quarters = sorted(quarterly_stats.items())
        quarters = [quarter for quarter, _ in sorted_quarters]
        means = [stats['mean'] for _, stats in sorted_quarters]
        counts = [stats['count'] for _, stats in sorted_quarters]
        
        # Create quarterly quality trend line
        plt.figure(figsize=(15, 6))
        plt.plot(quarters, means, marker='o', linestyle='-', color='skyblue')
        plt.title('Average Game Quality Score by Quarter', pad=20)
        plt.xlabel('Quarter')
        plt.ylabel('Average Quality Score')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add count labels
        for i, count in enumerate(counts):
            plt.text(i, means[i], f'n={count}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'quarterly_quality_trend.png'))
        plt.close()
        
        # 3. Monthly Quality Distribution
        monthly_scores = defaultdict(list)
        for game in games:
            month = f"{game['Year']}-{game['Month']:02d}"
            monthly_scores[month].append(game['Score'])
        
        # Create heatmap of monthly quality scores
        years = sorted(set(game['Year'] for game in games))
        months = range(1, 13)
        quality_matrix = np.zeros((len(years), 12))
        count_matrix = np.zeros((len(years), 12))
        
        for year_idx, year in enumerate(years):
            for month in months:
                month_key = f"{year}-{month:02d}"
                if month_key in monthly_scores:
                    quality_matrix[year_idx, month-1] = np.mean(monthly_scores[month_key])
                    count_matrix[year_idx, month-1] = len(monthly_scores[month_key])
        
        plt.figure(figsize=(15, 8))
        sns.heatmap(quality_matrix, 
                   annot=count_matrix.astype(int),
                   fmt='d',
                   cmap='YlOrRd',
                   xticklabels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                   yticklabels=years)
        plt.title('Monthly Game Quality Distribution', pad=20)
        plt.xlabel('Month')
        plt.ylabel('Year')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'monthly_quality_heatmap.png'))
        plt.close()
        
        # Generate insights
        insights = []
        insights.append("\nTemporal Analysis Insights:")
        insights.append(f"1. Total Games Analyzed: {len(games)}")
        insights.append("\nYearly Trends:")
        for year, stats in sorted_years:
            insights.append(f"- {year}:")
            insights.append(f"  * Average Score: {stats['mean']:.1f}")
            insights.append(f"  * Median Score: {stats['median']:.1f}")
            insights.append(f"  * Number of Games: {stats['count']}")
        
        insights.append("\nQuarterly Trends:")
        for quarter, stats in sorted_quarters:
            insights.append(f"- {quarter}:")
            insights.append(f"  * Average Score: {stats['mean']:.1f}")
            insights.append(f"  * Median Score: {stats['median']:.1f}")
            insights.append(f"  * Number of Games: {stats['count']}")
        
        # Save insights
        output_file = os.path.join(OUTPUT_DIR, 'temporal_analysis_insights.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(insights))
        
        logger.info(f"Analysis complete. Insights saved to {output_file}")
        
        # Print key insights
        print("\nKey Insights:")
        print(f"1. Total Games Analyzed: {len(games)}")
        print("\nYearly Trends:")
        for year, stats in sorted_years:
            print(f"- {year}:")
            print(f"  * Average Score: {stats['mean']:.1f}")
            print(f"  * Median Score: {stats['median']:.1f}")
            print(f"  * Number of Games: {stats['count']}")
        
    except Exception as e:
        logger.error(f"An error occurred during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    analyze_temporal_trends() 