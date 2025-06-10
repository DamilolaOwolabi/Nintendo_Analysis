# Nintendo Analysis Project

## Getting Started

### Prerequisites
- Git installed on your computer
- Python 3.x installed
- A code editor (VS Code, PyCharm, etc.)

### Downloading the Repository

#### Method 1: Using HTTPS (Recommended for beginners)
1. Open your terminal/command prompt
2. Navigate to the directory where you want to store the project
3. Run the following command:
   ```bash
   git clone https://github.com/DamilolaOwolabi/Nintendo_Analysis.git
   ```
4. Navigate into the project directory:
   ```bash
   cd Nintendo_Analysis
   ```

#### Method 2: Using SSH (For users with SSH keys set up)
1. Open your terminal/command prompt
2. Navigate to the directory where you want to store the project
3. Run the following command:
   ```bash
   git clone git@github.com:DamilolaOwolabi/Nintendo_Analysis.git
   ```
4. Navigate into the project directory:
   ```bash
   cd Nintendo_Analysis
   ```

### Setting Up the Project
1. Create a virtual environment (recommended):
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Project Structure
```
Nintendo_Analysis/
├── data/               # Data files
├── notebooks/          # Jupyter notebooks
├── results/           # Analysis results
├── src/               # Source code
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

### Running the Project
1. Make sure your virtual environment is activated
2. Navigate to the appropriate directory based on what you want to run
3. Follow the specific instructions in each notebook or script

### Contributing
1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request

### Contact
For any questions or issues, please open an issue in the GitHub repository.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

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