import pandas as pd
import numpy as np
from utils.database import setup_database, store_scraped_products

def generate_sample_products(count=20):
    """
    Generate sample product data for testing
    
    Parameters:
    -----------
    count : int, optional
        Number of sample products to generate (default: 20)
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing sample product data
    """
    np.random.seed(42)  # For reproducibility
    
    # Sample product names
    product_names = [
        "Fresh Milk 1L", "Whole Wheat Bread", "Organic Eggs (10 pcs)", 
        "Natural Yogurt 500g", "Ground Beef 500g", "Chicken Breast 1kg",
        "Tomatoes 1kg", "Apples 1kg", "Bananas 1kg", "Oranges 1kg",
        "Pasta 500g", "Rice 1kg", "Olive Oil 750ml", "Butter 250g",
        "Cheese 500g", "Coffee 200g", "Sugar 1kg", "Flour 1kg",
        "Potatoes 2kg", "Onions 1kg", "Carrots 1kg", "Cereal 500g",
        "Chocolate 100g", "Honey 350g", "Water 1.5L", "Orange Juice 1L",
        "Canned Tuna 150g", "Laundry Detergent 3L", "Toilet Paper 9 rolls",
        "Toothpaste 75ml"
    ]
    
    # Sample categories
    categories = [
        "Dairy", "Bakery", "Eggs", "Dairy", "Meat", "Poultry",
        "Vegetables", "Fruits", "Fruits", "Fruits",
        "Pantry", "Pantry", "Oils", "Dairy",
        "Dairy", "Beverages", "Pantry", "Pantry",
        "Vegetables", "Vegetables", "Vegetables", "Breakfast",
        "Sweets", "Pantry", "Beverages", "Beverages",
        "Canned Goods", "Household", "Household",
        "Personal Care"
    ]
    
    # Sample markets
    markets = ["KAM", "Vero", "Stokomak", "Tinex", "Ramstore"]
    
    # Generate random data
    data = []
    for i in range(min(count, len(product_names))):
        # Basic details
        name = product_names[i]
        category = categories[i]
        market = np.random.choice(markets)
        
        # Price details
        regular_price = np.round(np.random.uniform(50, 500), 2)
        has_discount = np.random.random() < 0.3  # 30% chance of discount
        
        if has_discount:
            discount_percent = np.random.choice([10, 15, 20, 25, 30, 50])
            price = np.round(regular_price * (1 - discount_percent / 100), 2)
            discount_type = np.random.choice(["Weekly Special", "Clearance", "Member Price"])
            discount_period = f"Until {np.random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])}"
        else:
            price = regular_price
            discount_percent = 0
            discount_type = None
            discount_period = None
        
        # Other details
        if "kg" in name or "g" in name:
            unit = "kg" if "kg" in name else "100g"
            unit_price = f"{np.round(price / (float(name.split()[1].replace('kg', '').replace('g', '')) / (1000 if 'g' in unit else 1)), 2)} MKD/{unit}"
        else:
            unit_price = None
        
        availability = np.random.choice(["In Stock", "Limited Stock", "Out of Stock"], p=[0.7, 0.2, 0.1])
        
        # Create product entry
        product = {
            "name": name,
            "price": price,
            "category": category,
            "market": market,
            "regular_price": regular_price if has_discount else None,
            "discounted_price": price if has_discount else None,
            "discount_percent": discount_percent if has_discount else None,
            "discount_type": discount_type,
            "discount_period": discount_period,
            "unit_price": unit_price,
            "availability": availability,
            "last_updated": "2025-04-18"
        }
        
        data.append(product)
    
    # Create and return DataFrame
    return pd.DataFrame(data)

def load_sample_data():
    """
    Load sample data into the database
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing the loaded sample data
    """
    # Generate sample data
    sample_data = generate_sample_products(30)
    
    # Set up database and store data
    setup_database()
    store_scraped_products(sample_data)
    
    return sample_data