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

def analyze_customer_satisfaction():
    logger.info("Analyzing relationship between game quality and customer satisfaction")
    
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
        
        # 1. Customer Satisfaction Analysis
        satisfaction_levels = {
            'Exceptional (90-100)': 0,
            'Very Satisfied (80-89)': 0,
            'Satisfied (70-79)': 0,
            'Neutral (60-69)': 0,
            'Dissatisfied (<60)': 0
        }
        
        for game in games:
            score = game['Score']
            if score >= 90:
                satisfaction_levels['Exceptional (90-100)'] += 1
            elif score >= 80:
                satisfaction_levels['Very Satisfied (80-89)'] += 1
            elif score >= 70:
                satisfaction_levels['Satisfied (70-79)'] += 1
            elif score >= 60:
                satisfaction_levels['Neutral (60-69)'] += 1
            else:
                satisfaction_levels['Dissatisfied (<60)'] += 1
        
        # Create satisfaction levels pie chart
        plt.figure(figsize=(10, 6))
        plt.pie(satisfaction_levels.values(),
                labels=satisfaction_levels.keys(),
                autopct='%1.1f%%',
                colors=['#2ecc71', '#27ae60', '#f1c40f', '#e67e22', '#e74c3c'])
        plt.title('Distribution of Games by Customer Satisfaction Level', pad=20)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'satisfaction_levels.png'))
        plt.close()
        
        # 2. Value Perception Analysis
        value_categories = {
            'Premium Value': 0,
            'High Value': 0,
            'Standard Value': 0,
            'Basic Value': 0
        }
        
        for game in games:
            score = game['Score']
            if score >= 85:
                value_categories['Premium Value'] += 1
            elif score >= 75:
                value_categories['High Value'] += 1
            elif score >= 65:
                value_categories['Standard Value'] += 1
            else:
                value_categories['Basic Value'] += 1
        
        # Create value perception bar chart
        plt.figure(figsize=(10, 6))
        bars = plt.bar(value_categories.keys(), value_categories.values(), color='skyblue')
        plt.title('Distribution of Games by Value Perception', pad=20)
        plt.xlabel('Value Category')
        plt.ylabel('Number of Games')
        plt.xticks(rotation=45)
        
        # Add count labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'value_perception.png'))
        plt.close()
        
        # 3. Price Sensitivity Analysis
        sensitivity_categories = {
            'Price Insensitive': 0,
            'Moderately Sensitive': 0,
            'Price Sensitive': 0
        }
        
        for game in games:
            score = game['Score']
            if score >= 85:
                sensitivity_categories['Price Insensitive'] += 1
            elif score >= 70:
                sensitivity_categories['Moderately Sensitive'] += 1
            else:
                sensitivity_categories['Price Sensitive'] += 1
        
        # Create price sensitivity pie chart
        plt.figure(figsize=(10, 6))
        plt.pie(sensitivity_categories.values(),
                labels=sensitivity_categories.keys(),
                autopct='%1.1f%%',
                colors=['#2ecc71', '#f1c40f', '#e74c3c'])
        plt.title('Distribution of Games by Price Sensitivity', pad=20)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'price_sensitivity.png'))
        plt.close()
        
        # Generate insights
        insights = []
        insights.append("\nCustomer Satisfaction Analysis:")
        insights.append(f"1. Total Games Analyzed: {len(games)}")
        insights.append("\nSatisfaction Levels:")
        for level, count in satisfaction_levels.items():
            percentage = (count / len(games)) * 100
            insights.append(f"- {level}: {count} games ({percentage:.1f}%)")
        
        insights.append("\nValue Perception:")
        for category, count in value_categories.items():
            percentage = (count / len(games)) * 100
            insights.append(f"- {category}: {count} games ({percentage:.1f}%)")
        
        insights.append("\nPrice Sensitivity:")
        for category, count in sensitivity_categories.items():
            percentage = (count / len(games)) * 100
            insights.append(f"- {category}: {count} games ({percentage:.1f}%)")
        
        # Save insights
        output_file = os.path.join(OUTPUT_DIR, 'customer_satisfaction_insights.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(insights))
        
        logger.info(f"Analysis complete. Insights saved to {output_file}")
        
        # Print key insights
        print("\nKey Insights:")
        print(f"1. Total Games Analyzed: {len(games)}")
        print("\nSatisfaction Levels:")
        for level, count in satisfaction_levels.items():
            percentage = (count / len(games)) * 100
            print(f"- {level}: {count} games ({percentage:.1f}%)")
        
        print("\nValue Perception:")
        for category, count in value_categories.items():
            percentage = (count / len(games)) * 100
            print(f"- {category}: {count} games ({percentage:.1f}%)")
        
        print("\nPrice Sensitivity:")
        for category, count in sensitivity_categories.items():
            percentage = (count / len(games)) * 100
            print(f"- {category}: {count} games ({percentage:.1f}%)")
        
    except Exception as e:
        logger.error(f"An error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    analyze_customer_satisfaction() 