import pandas as pd

def process_data(extracted_data_list):
    """
    Process and combine extracted data from multiple PDFs.
    
    Parameters:
    -----------
    extracted_data_list : list of pandas.DataFrame
        List of DataFrames containing extracted product data
        
    Returns:
    --------
    pandas.DataFrame
        Combined and processed data
    """
    if not extracted_data_list:
        return pd.DataFrame()
    
    # Combine all dataframes
    combined_data = pd.concat(extracted_data_list, ignore_index=True)
    
    # Clean the data
    clean_data_df = clean_data(combined_data)
    
    # Remove duplicates
    deduplicated_df = remove_duplicates(clean_data_df)
    
    # Standardize categories
    standardized_df = standardize_categories(deduplicated_df)
    
    return standardized_df

def clean_data(data):
    """
    Clean and standardize the data.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing extracted product data
        
    Returns:
    --------
    pandas.DataFrame
        Cleaned data
    """
    # Make a copy to avoid modifying original data
    df = data.copy()
    
    # Convert to lowercase for standardization
    df['name'] = df['name'].str.lower()
    
    # Remove leading/trailing whitespace
    df['name'] = df['name'].str.strip()
    
    # Ensure market names are consistent (Title case)
    df['market'] = df['market'].str.title()
    
    # Convert price to float if not already
    if df['price'].dtype != 'float64':
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    # Remove rows with missing essential data
    df = df.dropna(subset=['name', 'price', 'market'])
    
    # Remove entries with suspicious values (e.g., extremely high prices)
    df = df[df['price'] < 10000]  # Assuming no reasonable item costs more than $10,000
    df = df[df['price'] > 0]      # Remove free or negative-priced items
    
    # Capitalize product names for display
    df['name'] = df['name'].str.title()
    
    return df

def remove_duplicates(data):
    """
    Remove duplicate product entries.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing product data
        
    Returns:
    --------
    pandas.DataFrame
        Data with duplicates removed
    """
    # Make a copy
    df = data.copy()
    
    # Sort by market and price to keep the lowest price entry for exact duplicates
    df = df.sort_values(['market', 'price'])
    
    # Drop duplicates - keeping the first occurrence (lowest price) for the same product and market
    df = df.drop_duplicates(subset=['name', 'market'], keep='first')
    
    return df

def standardize_categories(data):
    """
    Standardize product categories.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing product data
        
    Returns:
    --------
    pandas.DataFrame
        Data with standardized categories
    """
    # Make a copy
    df = data.copy()
    
    # Ensure the category column exists
    if 'category' not in df.columns:
        df['category'] = 'Uncategorized'
    
    # Fill missing categories
    df['category'] = df['category'].fillna('Uncategorized')
    
    # Standardize category names to title case
    df['category'] = df['category'].str.title()
    
    # Map variations of categories to standard names
    category_mapping = {
        'Electronic': 'Electronics',
        'Electronics & Computers': 'Electronics',
        'Computer': 'Electronics',
        'Tv': 'Electronics',
        'Phone': 'Electronics',
        
        'Grocery': 'Groceries',
        'Food': 'Groceries',
        'Food Items': 'Groceries',
        
        'Fruit': 'Produce',
        'Fruits': 'Produce',
        'Vegetables': 'Produce',
        'Vegetable': 'Produce',
        'Fresh Produce': 'Produce',
        
        'Meats': 'Meat & Seafood',
        'Seafood': 'Meat & Seafood',
        'Fish': 'Meat & Seafood',
        
        'Dairy Products': 'Dairy',
        
        'Baked Goods': 'Bakery',
        'Bread': 'Bakery',
        
        'Drinks': 'Beverages',
        'Soda': 'Beverages',
        'Water': 'Beverages',
        'Coffee & Tea': 'Beverages',
        'Alcohol': 'Beverages',
        
        'Cleaning': 'Household',
        'Household Items': 'Household',
        'Household Supplies': 'Household',
        
        'Personal': 'Personal Care',
        'Beauty': 'Personal Care',
        'Health': 'Personal Care',
        'Health & Beauty': 'Personal Care',
        
        'Clothes': 'Clothing',
        'Apparel': 'Clothing',
        
        'Home': 'Home & Garden',
        'Garden': 'Home & Garden',
        'Furniture': 'Home & Garden',
        'Decor': 'Home & Garden',
        
        'Baby Products': 'Baby',
        'Baby Items': 'Baby',
        
        'Pet Supplies': 'Pet',
        'Pet Food': 'Pet',
        
        'Toys': 'Toys & Games',
        'Games': 'Toys & Games',
        
        'Sports': 'Sports & Outdoors',
        'Outdoors': 'Sports & Outdoors',
        'Fitness': 'Sports & Outdoors'
    }
    
    # Apply mapping to standardize categories
    for variant, standard in category_mapping.items():
        df.loc[df['category'] == variant, 'category'] = standard
    
    return df

def filter_data(data, category=None, min_price=None, max_price=None, markets=None):
    """
    Filter data based on category, price range, and markets.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing product data
    category : str, optional
        Category to filter by
    min_price : float, optional
        Minimum price
    max_price : float, optional
        Maximum price
    markets : list, optional
        List of markets to include
        
    Returns:
    --------
    pandas.DataFrame
        Filtered data
    """
    # Make a copy of the data
    filtered_data = data.copy()
    
    # Filter by category if specified
    if category is not None:
        filtered_data = filtered_data[filtered_data['category'] == category]
    
    # Filter by price range if specified
    if min_price is not None:
        filtered_data = filtered_data[filtered_data['price'] >= min_price]
    
    if max_price is not None:
        filtered_data = filtered_data[filtered_data['price'] <= max_price]
    
    # Filter by markets if specified
    if markets is not None and len(markets) > 0:
        filtered_data = filtered_data[filtered_data['market'].isin(markets)]
    
    return filtered_data

def search_products(data, query):
    """
    Search for products containing the query string.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing product data
    query : str
        Search query string
        
    Returns:
    --------
    pandas.DataFrame
        Filtered data containing only matching products
    """
    # Convert query to lowercase for case-insensitive search
    query_lower = query.lower()
    
    # Search in product names (case-insensitive)
    mask = data['name'].str.lower().str.contains(query_lower, na=False)
    
    # Also search in categories if available
    if 'category' in data.columns:
        mask = mask | data['category'].str.lower().str.contains(query_lower, na=False)
    
    # Also search in market names
    mask = mask | data['market'].str.lower().str.contains(query_lower, na=False)
    
    # Return filtered data
    return data[mask]