import pandas as pd
import re
import pdfplumber
from datetime import datetime

def extract_kam_prices_from_pdf(pdf_path):
    """
    Extract product prices from KAM supermarket PDF price list.
    
    Parameters:
    -----------
    pdf_path : str
        Path to the PDF file
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing extracted product details with the following columns:
        - name: Product name
        - price: Regular selling price
        - unit_price: Price per unit (e.g., per 100g)
        - description: Detailed product description
        - availability: Product availability in store
        - regular_price: Regular price (sometimes same as selling price)
        - discounted_price: Discounted price if available
        - discount_percent: Discount percentage if available
        - discount_type: Type of discount or promotion
        - discount_period: Duration of discount
        - category: Product category (derived from context)
        - market: Market name
        - last_updated: Date of price update
    """
    try:
        # Market name is KAM
        market = "KAM"
        update_date = None
        products = []
        
        with pdfplumber.open(pdf_path) as pdf:
            
            # Process each page
            for page in pdf.pages:
                page_text = page.extract_text()
                
                if not page_text:
                    continue
                
                # Extract the update date from the first page
                if update_date is None:
                    date_match = re.search(r'Датум и време на последно ажурирање на цените: (\d{2}\.\d{2}\.\d{4})', page_text)
                    if date_match:
                        date_str = date_match.group(1)
                        try:
                            update_date = datetime.strptime(date_str, '%d.%m.%Y').strftime('%Y-%m-%d')
                        except:
                            update_date = datetime.now().strftime('%Y-%m-%d')
                
                # Split into lines
                lines = page_text.split('\n')
                
                # Skip header lines
                product_lines = []
                for i, line in enumerate(lines):
                    if 'Назив на' in line and 'Продажна' in line:
                        # Skip header rows (there are usually 7 rows in the header)
                        product_lines = lines[i+7:]
                        break
                
                # Current category tracking
                current_category = "General"
                
                # Process the product lines
                for line in product_lines:
                    # Skip empty lines and header repetitions
                    if not line.strip() or 'Назив на' in line or 'Датум и време' in line:
                        continue
                    
                    # Check if this is a product line - they usually start with product name and have prices
                    # The KAM format has these fields: Name, Price, Unit Price, Description, Availability, Regular Price, Discounted Price
                    
                    # Match pattern for product line
                    # Example: "ЛАЈБИЦИ СЛИБО 23ден. 100 гр = 9.2 ЛАЈБИЦИ ДИЕТ Да 23ден."
                    # First, let's try to match the price and then extract the name and description
                    
                    # Price is usually followed by "ден."
                    price_match = re.search(r'(\d+)ден\.', line)
                    if price_match:
                        # Extract the product name (everything before the price)
                        line_parts = line.split(price_match.group(0), 1)
                        if len(line_parts) >= 2:
                            # Product name is at the beginning of the line
                            product_name = line_parts[0].strip()
                            
                            # Rest of the line contains unit price, description, availability, etc.
                            rest_of_line = line_parts[1].strip()
                            
                            # Extract unit price (e.g., "100 гр = 9.2 ден.")
                            unit_price_match = re.search(r'(\d+) гр = ([\d\.]+)', rest_of_line)
                            unit_price = None
                            if unit_price_match:
                                unit_price = unit_price_match.group(0)
                                
                            # Extract description (after unit price)
                            description = None
                            if unit_price and unit_price in rest_of_line:
                                desc_parts = rest_of_line.split(unit_price, 1)
                                if len(desc_parts) >= 2:
                                    # Split by "Да" (availability indicator)
                                    if "Да" in desc_parts[1]:
                                        description = desc_parts[1].split("Да")[0].strip()
                            
                            # Extract regular price
                            regular_price_match = re.search(r'Да\s+(\d+)ден\.', rest_of_line)
                            regular_price = None
                            if regular_price_match:
                                regular_price = regular_price_match.group(1)
                            
                            # Look for discount price (not all products have it)
                            discount_price = None
                            discount_percent = None
                            discount_type = None
                            discount_period = None
                            
                            # Check if there's any discount information
                            if "попуст" in rest_of_line.lower():
                                # Try to find discount information
                                discount_match = re.search(r'попуст\s*\((%)\)\s*(\d+)', rest_of_line, re.IGNORECASE)
                                if discount_match:
                                    discount_percent = discount_match.group(2)
                                    
                                # Try to find discounted price
                                discount_price_match = re.search(r'Цена со\s+попуст\s+(\d+)', rest_of_line, re.IGNORECASE)
                                if discount_price_match:
                                    discount_price = discount_price_match.group(1)
                            
                            # Add to products list
                            products.append({
                                'name': product_name,
                                'price': price_match.group(1),
                                'unit_price': unit_price,
                                'description': description,
                                'availability': "Да",  # Almost all products have "Да" (Yes) availability
                                'regular_price': regular_price,
                                'discounted_price': discount_price,
                                'discount_percent': discount_percent,
                                'discount_type': discount_type,
                                'discount_period': discount_period,
                                'category': derive_category_from_name(product_name),
                                'market': market,
                                'last_updated': update_date or datetime.now().strftime('%Y-%m-%d')
                            })
        
        # Convert to DataFrame
        if products:
            df = pd.DataFrame(products)
            # Convert price to float
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
            # Filter out invalid prices
            df = df[df['price'].notna()]
            return df
        else:
            return pd.DataFrame()
    
    except Exception as e:
        print(f"Error extracting data from KAM PDF: {e}")
        return pd.DataFrame()

def derive_category_from_name(product_name):
    """
    Infer product category from its name based on common keywords.
    
    Parameters:
    -----------
    product_name : str
        Name of the product
        
    Returns:
    --------
    str
        Inferred category
    """
    # Define category keywords
    category_keywords = {
        'Хлеб и пекарски производи': ['леб', 'кифл', 'пекар', 'тост', 'брускет', 'пченкар'],
        'Слатки и бонбони': ['чокол', 'бонбон', 'желе', 'торт', 'крем', 'слатк', 'какао'],
        'Житарки и мусли': ['житарк', 'мусли', 'корнфлекс'],
        'Тестенини': ['фиде', 'тестен'],
        'Месо и месни производи': ['месо', 'колбас', 'салам', 'пршут', 'сувомес'],
        'Млеко и млечни производи': ['млеко', 'јогурт', 'сирењ', 'кашкав', 'павлак'],
        'Овошје и зеленчук': ['овошј', 'зеленчук', 'јаболк', 'домат', 'пипер'],
        'Пијалоци': ['пијалок', 'сок', 'вода', 'кафе', 'чај'],
        'Производи за домаќинство': ['средство', 'чист', 'детерг', 'перал', 'сапун', 'шампон'],
        'Храна за миленици': ['храна за', 'миленич']
    }
    
    # Check each category
    product_lower = product_name.lower()
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword.lower() in product_lower:
                return category
    
    # Default category
    return "Останато"

def kam_pdf_to_csv(pdf_path, csv_path):
    """
    Convert KAM PDF price list to CSV file.
    
    Parameters:
    -----------
    pdf_path : str
        Path to the PDF file
    csv_path : str
        Path where to save the CSV file
        
    Returns:
    --------
    bool
        True if conversion was successful, False otherwise
    """
    try:
        df = extract_kam_prices_from_pdf(pdf_path)
        if not df.empty:
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            return True
        return False
    except Exception as e:
        print(f"Error converting KAM PDF to CSV: {e}")
        return False