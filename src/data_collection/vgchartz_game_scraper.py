import csv
import os
import logging
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Using a more direct URL
VGCHARTZ_URL = "https://www.vgchartz.com/games/games.php?console=Nintendo+Switch&region=All&order=Sales&showtotalsales=1&showpalsales=0&showjapansales=0&showothersales=0&showpublisher=0&showdeveloper=0&showreleasedate=1&showlastupdate=1&showvgchartzscore=1&showcriticscore=1&showuserscore=1&showshipped=1&results=200"

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw', 'nintendo_game_sales.csv')

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.68 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.68 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
    ]
    return random.choice(user_agents)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f"--user-agent={get_random_user_agent()}")
    
    # Add additional options to make the browser more realistic
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Add additional stability options
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    chrome_options.add_argument("--disable-site-isolation-trials")

    # Add additional headers
    chrome_options.add_argument("--accept-lang=en-US,en;q=0.9")
    chrome_options.add_argument("--sec-ch-ua-platform=Windows")
    chrome_options.add_argument("--sec-ch-ua-mobile=?0")
    chrome_options.add_argument("--sec-ch-ua=Google Chrome;v=137")

    chromedriver_path = os.path.expanduser('~/bin/chromedriver')
    if not os.path.exists(chromedriver_path):
        logger.error(f"ChromeDriver not found at {chromedriver_path}. Please download ChromeDriver and place it in ~/bin/")
        return None
    
    service = Service(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=chrome_options)

def scrape_vgchartz_game_sales():
    logger.info(f"Scraping VGChartz game sales from {VGCHARTZ_URL}")
    driver = setup_driver()
    
    if not driver:
        return

    try:
        # Execute CDP commands to make the browser more realistic
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": get_random_user_agent(),
            "platform": "Windows",
            "acceptLanguage": "en-US,en;q=0.9"
        })
        
        # Add additional CDP commands to make the browser more realistic
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });
            '''
        })

        # Set additional headers
        driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
            'headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Ch-Ua': '"Google Chrome";v="137"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
        })

        # Load the page with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add random delay before each attempt
                time.sleep(random.uniform(2, 5))
                
                driver.get(VGCHARTZ_URL)
                logger.info(f"Page loaded (attempt {attempt + 1}/{max_retries}), waiting for table...")
                
                # Add a random delay to mimic human behavior
                time.sleep(random.uniform(3, 7))
                
                # Wait for the page to load
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Print page title for debugging
                logger.info(f"Page title: {driver.title}")
                
                # Try to find the table
                try:
                    table = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'chart'))
                    )
                    break  # If we found the table, break the retry loop
                except TimeoutException:
                    if attempt == max_retries - 1:  # Last attempt
                        logger.error("Could not find table with class 'chart'")
                        logger.info("Page source:")
                        logger.info(driver.page_source[:1000])  # Print first 1000 chars of page source
                        return
                    logger.warning(f"Table not found on attempt {attempt + 1}, retrying...")
                    continue
                    
            except WebDriverException as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise
                logger.warning(f"WebDriver error on attempt {attempt + 1}: {str(e)}")
                time.sleep(random.uniform(3, 7))  # Random wait before retry
                continue

        rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # Skip header
        data = []
        for row in rows:
            try:
                cols = [col.text.strip() for col in row.find_elements(By.TAG_NAME, 'td')]
                if not cols or len(cols) < 7:
                    logger.warning(f'Skipping row with insufficient columns: {cols}')
                    continue
                data.append({
                    'Game': cols[1],
                    'Platform': cols[2],
                    'Publisher': cols[3],
                    'Developer': cols[4],
                    'Total Sales (M)': cols[5],
                    'Release Date': cols[6]
                })
            except Exception as e:
                logger.warning(f"Error processing row: {str(e)}")
                continue

        if not data:
            logger.warning('No Nintendo game data found.')
            return

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"Nintendo game sales data saved to {OUTPUT_FILE}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.warning(f"Error while closing driver: {str(e)}")

if __name__ == "__main__":
    scrape_vgchartz_game_sales() 