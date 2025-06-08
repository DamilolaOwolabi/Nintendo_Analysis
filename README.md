# Nintendo Price Analysis Project

## Project Overview
This project analyzes the potential impact of Nintendo's proposed price increase from $60 to $90 for their video games. The analysis focuses on multiple aspects including market impact, customer sentiment, and financial implications.

## Research Questions
1. How would a price increase from $60 to $90 affect Nintendo's market position and customer base?
2. What is the correlation between social media sentiment and game sales?
3. How do Nintendo's pricing strategies compare with competitors?
4. What is the potential impact on piracy rates and customer behavior?

## Data Sources
- Historical game sales data
- Social media sentiment analysis (Twitter, Reddit)
- Competitor pricing data
- Piracy and emulator download statistics
- Customer survey data

## Project Structure
```
├── data/                  # Raw and processed data
├── src/                   # Source code
│   ├── data_collection/   # Data scraping and collection scripts
│   ├── analysis/         # Data analysis scripts
│   └── visualization/    # Data visualization scripts
├── notebooks/            # Jupyter notebooks for analysis
└── results/             # Analysis results and visualizations
```

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables for API access:
- Create a `.env` file with necessary API keys
- Required APIs: Twitter, Reddit

## Data Collection
The project collects data from multiple sources:
- Web scraping of game sales data
- Social media API integration
- Public datasets
- Customer surveys

## Analysis Methods
- Sentiment analysis of social media data
- Price elasticity analysis
- Competitor comparison
- Piracy impact assessment
- Customer behavior modeling

## Results
Results will be documented in the `results/` directory, including:
- Data visualizations
- Statistical analysis
- Predictive models
- Recommendations 