import pdfplumber
import pandas as pd
import re
import os

def extract_prices_from_pdf(pdf_path):
    """
    Extract product prices and details from PDF files.
    
    Parameters:
    -----------
    pdf_path : str
        Path to the PDF file
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing extracted product details
    """
    try:
        products = []
        market = extract_market_from_filename(os.path.basename(pdf_path))
        
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            
            # Extract text from all pages
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            
            # If market is still None, try to extract from content
            if not market:
                market = extract_market_from_content(full_text)
            
            # Extract products information from text
            extracted_products = extract_products_from_text(full_text)
            
            # Add market information to each product
            for product in extracted_products:
                product['market'] = market
                # Attempt to extract category if not already present
                if 'category' not in product or not product['category']:
                    product['category'] = extract_category(product['name'], full_text)
                products.append(product)
        
        # Create DataFrame from extracted products
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
        print(f"Error extracting data from PDF: {e}")
        return pd.DataFrame()

def extract_market_from_filename(filename):
    """Extract market name from the PDF filename."""
    # Remove extension and split by common separators
    name = os.path.splitext(filename)[0]
    
    # Common market names to check for
    common_markets = ['walmart', 'target', 'costco', 'kroger', 'aldi', 'lidl', 
                     'carrefour', 'tesco', 'sainsbury', 'edeka', 'rewe', 
                     'auchan', 'leclerc', 'mercadona', 'jumbo', 'albert heijn']
    
    for market in common_markets:
        if market.lower() in name.lower():
            return market.title()
    
    # If no match found, use the filename as market name
    return name

def extract_market_from_content(text):
    """Extract market name from the PDF content."""
    # Look for market name in header or footer
    lines = text.split('\n')
    
    # Check first and last few lines for market name
    potential_header_footer = lines[:3] + lines[-3:]
    header_footer_text = ' '.join(potential_header_footer).lower()
    
    # Common market names to check for
    common_markets = ['walmart', 'target', 'costco', 'kroger', 'aldi', 'lidl', 
                     'carrefour', 'tesco', 'sainsbury', 'edeka', 'rewe', 
                     'auchan', 'leclerc', 'mercadona', 'jumbo', 'albert heijn']
    
    for market in common_markets:
        if market.lower() in header_footer_text:
            return market.title()
    
    # If no match found in header/footer, look in whole document
    for market in common_markets:
        if market.lower() in text.lower():
            return market.title()
    
    # Default to "Unknown Market" if no match found
    return "Unknown Market"

def extract_products_from_text(text):
    """
    Extract product information from text using various patterns.
    
    This function tries multiple patterns to extract:
    - Product name
    - Price
    - Category (if available)
    """
    products = []
    
    # Pattern for product entries: product name followed by price
    # This pattern looks for product descriptions followed by price patterns like $XX.XX
    patterns = [
        r'([A-Za-z0-9][\w\s,&\-\'\.]+)\$([\d]+\.[\d]{2})',  # Name followed by $XX.XX
        r'([A-Za-z0-9][\w\s,&\-\'\.]+)[\s]*\$([\d]+\.[\d]{2})',  # Name with spaces then $XX.XX
        r'([A-Za-z0-9][\w\s,&\-\'\.]+)[\s]*\$\s*([\d]+\.[\d]{2})',  # Name with spaces then $ XX.XX
        r'([A-Za-z0-9][\w\s,&\-\'\.]+)[\s]*([\d]+\.[\d]{2})\s*\$',  # Name with price then $
        r'([A-Za-z0-9][\w\s,&\-\'\.]+)[\s]*\$\s*([\d]+)',  # Name with spaces then $ XX
    ]
    
    # Try each pattern
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            name = match[0].strip()
            price = match[1].strip()
            
            # Skip if name is too short (likely a false match)
            if len(name) < 3:
                continue
                
            # Skip if price is unreasonable
            try:
                price_float = float(price)
                if price_float <= 0 or price_float > 10000:
                    continue
            except ValueError:
                continue
            
            # Add product to list
            products.append({
                'name': name,
                'price': price,
            })
    
    # Try to find structured tables
    lines = text.split('\n')
    for i, line in enumerate(lines):
        # Look for lines that have both text and numbers with dollar signs
        if '$' in line and re.search(r'[A-Za-z]{3,}', line):
            # Split by whitespace
            parts = re.split(r'\s{2,}', line)
            if len(parts) >= 2:
                name_parts = []
                price = None
                
                for part in parts:
                    # Check if part contains a price
                    price_match = re.search(r'\$([\d]+\.[\d]{2})', part)
                    if price_match:
                        price = price_match.group(1)
                    elif len(part.strip()) > 2:  # If not a price and not too short
                        name_parts.append(part.strip())
                
                if price and name_parts:
                    name = ' '.join(name_parts)
                    products.append({
                        'name': name,
                        'price': price,
                    })
    
    return products

def extract_category(product_name, text):
    """Attempt to extract product category based on product name or surrounding text."""
    # Common categories and keywords associated with them
    categories = {
        'Electronics': ['tv', 'television', 'phone', 'smartphone', 'laptop', 'computer', 'tablet', 'camera', 'headphone'],
        'Groceries': ['bread', 'milk', 'cheese', 'yogurt', 'egg', 'cereal', 'rice', 'pasta', 'flour', 'sugar', 'oil'],
        'Produce': ['apple', 'banana', 'orange', 'grape', 'strawberry', 'vegetable', 'tomato', 'potato', 'onion', 'carrot'],
        'Meat & Seafood': ['beef', 'chicken', 'pork', 'fish', 'salmon', 'shrimp', 'meat', 'seafood', 'steak', 'ground'],
        'Dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'ice cream'],
        'Bakery': ['bread', 'cake', 'cookie', 'pastry', 'muffin', 'bagel'],
        'Beverages': ['water', 'soda', 'juice', 'coffee', 'tea', 'drink', 'beer', 'wine', 'alcohol'],
        'Household': ['cleaner', 'detergent', 'soap', 'paper towel', 'toilet paper', 'trash bag'],
        'Personal Care': ['shampoo', 'conditioner', 'toothpaste', 'soap', 'deodorant', 'razor', 'lotion'],
        'Clothing': ['shirt', 'pant', 'dress', 'sock', 'underwear', 'jacket', 'sweater', 'shoe'],
        'Home & Garden': ['furniture', 'decor', 'plant', 'garden', 'tool', 'bedding', 'curtain'],
        'Baby': ['diaper', 'formula', 'baby food', 'wipe', 'baby'],
        'Pet': ['pet food', 'dog', 'cat', 'pet', 'litter'],
        'Toys & Games': ['toy', 'game', 'puzzle', 'doll', 'action figure'],
        'Sports & Outdoors': ['sport', 'outdoor', 'exercise', 'fitness', 'camping', 'hiking']
    }
    
    # Convert product name to lowercase for matching
    product_lower = product_name.lower()
    
    # Check if any category keywords appear in the product name
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in product_lower:
                return category
    
    # If no match found, look for the product name in the text and check surrounding lines
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if product_name in line:
            # Check 3 lines before and after for category headers
            context_lines = lines[max(0, i-3):min(len(lines), i+4)]
            context_text = ' '.join(context_lines).lower()
            
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword.lower() in context_text:
                        return category
            
            # Look for category headers (usually short lines, all caps)
            for line in context_lines:
                if line.isupper() and 3 < len(line) < 30 and line.strip() != product_name:
                    # This might be a category header
                    return line.strip()
    
    # Default to "Uncategorized" if no match found
    return "Uncategorized"