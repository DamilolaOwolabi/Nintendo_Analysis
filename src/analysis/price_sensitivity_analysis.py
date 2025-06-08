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

def calculate_price_elasticity(price_changes, sales_changes):
    """Calculate price elasticity of demand."""
    if not price_changes or not sales_changes:
        return None
    
    # Calculate percentage changes
    price_pct_changes = np.array(price_changes) / 100
    sales_pct_changes = np.array(sales_changes) / 100
    
    # Calculate elasticity
    elasticity = np.mean(sales_pct_changes / price_pct_changes)
    return elasticity

def analyze_price_sensitivity():
    logger.info("Analyzing price sensitivity and elasticity")
    
    try:
        # Read the data
        games = []
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    games.append({
                        'Game': row['Game'],
                        'Score': float(row['OpenCritic Score']),
                        'Price': float(row.get('Price', 0)),
                        'Sales': float(row.get('Sales', 0)),
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
        
        # 1. Price Distribution Analysis
        prices = [game['Price'] for game in games if game['Price'] > 0]
        
        plt.figure(figsize=(10, 6))
        sns.histplot(prices, bins=20, color='skyblue')
        plt.title('Distribution of Game Prices', pad=20)
        plt.xlabel('Price ($)')
        plt.ylabel('Number of Games')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'price_distribution.png'))
        plt.close()
        
        # 2. Price vs Quality Analysis
        plt.figure(figsize=(10, 6))
        plt.scatter([game['Price'] for game in games if game['Price'] > 0],
                   [game['Score'] for game in games if game['Price'] > 0],
                   alpha=0.6, color='skyblue')
        plt.title('Relationship Between Price and Quality', pad=20)
        plt.xlabel('Price ($)')
        plt.ylabel('Quality Score')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add trend line
        x = np.array([game['Price'] for game in games if game['Price'] > 0])
        y = np.array([game['Score'] for game in games if game['Price'] > 0])
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        plt.plot(x, p(x), "r--", alpha=0.8)
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'price_vs_quality.png'))
        plt.close()
        
        # 3. Price vs Sales Analysis
        plt.figure(figsize=(10, 6))
        plt.scatter([game['Price'] for game in games if game['Price'] > 0 and game['Sales'] > 0],
                   [game['Sales'] for game in games if game['Price'] > 0 and game['Sales'] > 0],
                   alpha=0.6, color='skyblue')
        plt.title('Relationship Between Price and Sales', pad=20)
        plt.xlabel('Price ($)')
        plt.ylabel('Sales (millions)')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add trend line
        x = np.array([game['Price'] for game in games if game['Price'] > 0 and game['Sales'] > 0])
        y = np.array([game['Sales'] for game in games if game['Price'] > 0 and game['Sales'] > 0])
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        plt.plot(x, p(x), "r--", alpha=0.8)
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'price_vs_sales.png'))
        plt.close()
        
        # 4. Price Elasticity Analysis
        # Group games by price ranges
        price_ranges = {
            'Budget (<$30)': (0, 30),
            'Mid-Range ($30-$50)': (30, 50),
            'Premium ($50-$70)': (50, 70),
            'High-End (>$70)': (70, float('inf'))
        }
        
        price_range_stats = defaultdict(lambda: {'games': [], 'sales': [], 'scores': []})
        
        for game in games:
            if game['Price'] > 0:
                for range_name, (min_price, max_price) in price_ranges.items():
                    if min_price <= game['Price'] < max_price:
                        price_range_stats[range_name]['games'].append(game['Game'])
                        price_range_stats[range_name]['sales'].append(game['Sales'])
                        price_range_stats[range_name]['scores'].append(game['Score'])
        
        # Create price range analysis
        plt.figure(figsize=(12, 6))
        ranges = list(price_ranges.keys())
        avg_sales = [np.mean(stats['sales']) for stats in price_range_stats.values()]
        avg_scores = [np.mean(stats['scores']) for stats in price_range_stats.values()]
        counts = [len(stats['games']) for stats in price_range_stats.values()]
        
        x = np.arange(len(ranges))
        width = 0.35
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()
        
        bars1 = ax1.bar(x - width/2, avg_sales, width, label='Average Sales', color='skyblue')
        bars2 = ax2.bar(x + width/2, avg_scores, width, label='Average Score', color='lightgreen')
        
        ax1.set_xlabel('Price Range')
        ax1.set_ylabel('Average Sales (millions)')
        ax2.set_ylabel('Average Quality Score')
        
        plt.title('Price Range Analysis', pad=20)
        ax1.set_xticks(x)
        ax1.set_xticklabels(ranges, rotation=45, ha='right')
        
        # Add count labels
        for i, count in enumerate(counts):
            ax1.text(i, avg_sales[i], f'n={count}',
                    ha='center', va='bottom')
        
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'price_range_analysis.png'))
        plt.close()
        
        # Generate insights
        insights = []
        insights.append("\nPrice Sensitivity Analysis Insights:")
        insights.append(f"1. Total Games Analyzed: {len(games)}")
        
        insights.append("\nPrice Range Analysis:")
        for range_name, stats in price_range_stats.items():
            insights.append(f"- {range_name}:")
            insights.append(f"  * Number of Games: {len(stats['games'])}")
            insights.append(f"  * Average Sales: {np.mean(stats['sales']):.2f} million")
            insights.append(f"  * Average Score: {np.mean(stats['scores']):.1f}")
        
        # Calculate price elasticity
        price_changes = []
        sales_changes = []
        for i in range(1, len(games)):
            if games[i]['Price'] > 0 and games[i-1]['Price'] > 0:
                price_change = ((games[i]['Price'] - games[i-1]['Price']) / games[i-1]['Price']) * 100
                sales_change = ((games[i]['Sales'] - games[i-1]['Sales']) / games[i-1]['Sales']) * 100
                price_changes.append(price_change)
                sales_changes.append(sales_change)
        
        elasticity = calculate_price_elasticity(price_changes, sales_changes)
        if elasticity is not None:
            insights.append(f"\nPrice Elasticity: {elasticity:.2f}")
            if elasticity < -1:
                insights.append("The demand is elastic (price sensitive)")
            elif elasticity > -1:
                insights.append("The demand is inelastic (price insensitive)")
            else:
                insights.append("The demand is unit elastic")
        
        # Save insights
        output_file = os.path.join(OUTPUT_DIR, 'price_sensitivity_insights.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(insights))
        
        logger.info(f"Analysis complete. Insights saved to {output_file}")
        
        # Print key insights
        print("\nKey Insights:")
        print(f"1. Total Games Analyzed: {len(games)}")
        print("\nPrice Range Analysis:")
        for range_name, stats in price_range_stats.items():
            print(f"- {range_name}:")
            print(f"  * Number of Games: {len(stats['games'])}")
            print(f"  * Average Sales: {np.mean(stats['sales']):.2f} million")
            print(f"  * Average Score: {np.mean(stats['scores']):.1f}")
        
        if elasticity is not None:
            print(f"\nPrice Elasticity: {elasticity:.2f}")
            if elasticity < -1:
                print("The demand is elastic (price sensitive)")
            elif elasticity > -1:
                print("The demand is inelastic (price insensitive)")
            else:
                print("The demand is unit elastic")
        
    except Exception as e:
        logger.error(f"An error occurred during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    analyze_price_sensitivity() 