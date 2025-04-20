import pandas as pd
import trafilatura
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

def scrape_vero_prices():
    """
    Scrape product prices from Vero's price list

    Returns:
    --------
    pandas.DataFrame
        DataFrame containing product information (name, price, category)
    """
    url = "https://pricelist.vero.com.mk/91_2.html"

    try:
        # Send a request to the website
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        products = []
        market_name = "Vero"

        # Find all table rows
        rows = soup.find_all('tr')
        current_category = "General"

        for row in rows:
            # Look for category headers (typically in th elements)
            th = row.find('th')
            if th and th.text.strip():
                current_category = th.text.strip()
                continue

            # Extract product information from td elements
            cells = row.find_all('td')
            if len(cells) >= 2:
                name = cells[0].text.strip()
                price_text = cells[-1].text.strip()

                # Clean up price text and convert to float
                price_clean = re.sub(r'[^\d.,]', '', price_text)
                price_clean = price_clean.replace(',', '.')

                try:
                    price = float(price_clean)
                    # Only add products with valid prices and within reasonable range
                    if 0 < price < 1000000:  # Limit to prices under 1 million
                        products.append({
                            'name': name,
                            'price': price,
                            'unit_price': None,  # Vero doesn't provide unit prices
                            'category': current_category,
                            'market': market_name,
                            'description': None,
                            'availability': 'Yes',
                            'regular_price': price,
                            'discounted_price': None,
                            'discount_percent': None,
                            'discount_type': None,
                            'discount_period': None,
                            'last_updated': datetime.now().strftime('%Y-%m-%d'),
                            'source_document': url
                        })
                except ValueError:
                    continue

        return pd.DataFrame(products)

    except Exception as e:
        print(f"Error scraping Vero prices: {e}")
        return pd.DataFrame()

def scrape_stokomak_prices():
    """
    Scrape product prices from stokomak.com.mk/proverka-na-ceni/

    Returns:
    --------
    pandas.DataFrame
        DataFrame containing product information (name, price, category)
    """
    url = "https://stokomak.com.mk/proverka-na-ceni/"

    # Send a request to the website
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table with product prices
    tables = soup.find_all('table', class_='table')

    products = []
    market_name = "Stokomak"

    if tables:
        # Process each table (there might be multiple tables for different categories)
        for table in tables:
            # Try to identify category from headings near the table
            category = "General"
            prev_elem = table.find_previous(['h2', 'h3', 'h4'])
            if prev_elem:
                category = prev_elem.text.strip()

            # Process table rows
            rows = table.find_all('tr')

            # Skip header row if present
            for row in rows[1:]:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    # Extract product name and price
                    name = cells[0].text.strip()

                    # Extract price and handle formatting
                    price_text = cells[1].text.strip()
                    # Remove non-numeric characters except decimal point
                    price_clean = re.sub(r'[^\d.,]', '', price_text)
                    # Replace comma with period for decimal point
                    price_clean = price_clean.replace(',', '.')

                    try:
                        price = float(price_clean)
                        products.append({
                            'name': name,
                            'price': price,
                            'category': category,
                            'market': market_name,
                            'last_updated': datetime.now().strftime('%Y-%m-%d')
                        })
                    except ValueError:
                        # Skip rows where price cannot be parsed
                        continue

    # If no tables were found or no products extracted, try an alternative approach
    if not products:
        # Try to find JSON data in script tags
        script_tags = soup.find_all('script')
        for script in script_tags:
            script_content = script.string
            if script_content and 'productName' in script_content:
                try:
                    # Try to find JSON objects in the script
                    json_str = re.search(r'\{.*"productName".*\}', script_content)
                    if json_str:
                        product_data = json.loads(json_str.group(0))
                        name = product_data.get('productName', '')
                        price_str = product_data.get('price', '0')

                        try:
                            price = float(price_str)
                            products.append({
                                'name': name,
                                'price': price,
                                'category': 'General',
                                'market': market_name,
                                'last_updated': datetime.now().strftime('%Y-%m-%d')
                            })
                        except ValueError:
                            continue
                except (json.JSONDecodeError, AttributeError):
                    continue

    # Final fallback: use trafilatura to extract text content
    if not products:
        # Extract text content
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)

        if text:
            # Look for price patterns in the text
            lines = text.split('\n')

            current_category = "General"
            for line in lines:
                # Check if line looks like a category heading
                if line.isupper() or (len(line) < 40 and not line.strip().endswith('ден')):
                    current_category = line.strip()
                    continue

                # Look for product price pattern (Product name followed by price)
                price_match = re.search(r'(.*?)\s+(\d+[.,]?\d*)\s*ден', line)
                if price_match:
                    name = price_match.group(1).strip()
                    price_str = price_match.group(2).replace(',', '.')

                    try:
                        price = float(price_str)
                        products.append({
                            'name': name,
                            'price': price,
                            'category': current_category,
                            'market': market_name,
                            'last_updated': datetime.now().strftime('%Y-%m-%d')
                        })
                    except ValueError:
                        continue

    # Convert to DataFrame
    if products:
        return pd.DataFrame(products)
    else:
        return pd.DataFrame(columns=['name', 'price', 'category', 'market', 'last_updated'])