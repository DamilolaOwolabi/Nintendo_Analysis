import requests
from bs4 import BeautifulSoup
import csv
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

VGCHARTZ_URL = "https://www.vgchartz.com/analysis/platform_totals/"

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw', 'nintendo_console_sales.csv')

NINTENDO_CONSOLES = [
    'Switch', 'Wii', 'Wii U', '3DS', 'DS', 'GameCube', 'N64', 'SNES', 'NES', 'Game Boy', 'Game Boy Advance', 'Virtual Boy'
]

def scrape_vgchartz_console_sales():
    logger.info(f"Scraping VGChartz console sales from {VGCHARTZ_URL}")
    response = requests.get(VGCHARTZ_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table', {'class': 'chart'})
    if not table:
        logger.error('Could not find sales table on VGChartz page.')
        return

    rows = table.find_all('tr')[1:]  # Skip header
    data = []
    for row in rows:
        cols = [col.text.strip() for col in row.find_all('td')]
        if not cols or len(cols) < 7:
            logger.warning(f'Skipping row with insufficient columns: {cols}')
            continue
        name = cols[1]
        if any(console in name for console in NINTENDO_CONSOLES):
            data.append({
                'Console': name,
                'North America (M)': cols[2],
                'Europe (M)': cols[3],
                'Japan (M)': cols[4],
                'Rest of World (M)': cols[5],
                'Total Sales (M)': cols[6]
            })

    if not data:
        logger.warning('No Nintendo console data found.')
        return

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    logger.info(f"Nintendo console sales data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_vgchartz_console_sales() 