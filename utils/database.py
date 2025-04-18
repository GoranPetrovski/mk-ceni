import os
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database using environment variables.
    
    Returns:
    --------
    connection: psycopg2.connection
        A connection to the PostgreSQL database.
    """
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Connect to the database
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def setup_database():
    """
    Sets up the necessary database tables if they don't exist yet.
    
    Returns:
    --------
    bool
        True if setup was successful, False otherwise.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create markets table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS markets (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                logo_url VARCHAR(512),
                website VARCHAR(512)
            )
        """)
        
        # Create products table with the new schema for KAM data
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                price NUMERIC(15, 2) NOT NULL,
                unit_price VARCHAR(255),
                category VARCHAR(255),
                market_id INTEGER REFERENCES markets(id),
                image_url VARCHAR(512),
                description TEXT,
                availability VARCHAR(50),
                regular_price NUMERIC(15, 2),
                discounted_price NUMERIC(15, 2),
                discount_percent NUMERIC(5, 2),
                discount_type VARCHAR(255),
                discount_period VARCHAR(255),
                last_updated DATE,
                source_document VARCHAR(255)
            )
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database setup error: {e}")
        return False

def store_scraped_products(products_df):
    """
    Stores scraped products data into the database.
    
    Parameters:
    -----------
    products_df : pandas.DataFrame
        DataFrame containing product data (name, price, category, market, last_updated)
    
    Returns:
    --------
    bool
        True if storage was successful, False otherwise.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Ensure tables exist
        setup_database()
        
        # First, make sure all markets exist
        unique_markets = products_df['market'].unique()
        
        for market in unique_markets:
            # Check if market exists
            cur.execute("SELECT id FROM markets WHERE name = %s", (market,))
            market_id = cur.fetchone()
            
            # If market doesn't exist, create it
            if not market_id:
                cur.execute(
                    "INSERT INTO markets (name) VALUES (%s) RETURNING id",
                    (market,)
                )
                market_id = cur.fetchone()
            
            # Get the market ID integer
            market_id_value = market_id[0] if market_id else None
            
            # Add products for this market
            market_products = products_df[products_df['market'] == market]
            
            # Prepare batch insert
            product_data = []
            for _, row in market_products.iterrows():
                # Handle the new KAM fields if they exist
                product_data.append((
                    row['name'],
                    row['price'],
                    row.get('unit_price', None),
                    row.get('category', 'Uncategorized'),
                    market_id_value,
                    row.get('image_url', None),
                    row.get('description', None),
                    row.get('availability', None),
                    row.get('regular_price', None),
                    row.get('discounted_price', None),
                    row.get('discount_percent', None),
                    row.get('discount_type', None),
                    row.get('discount_period', None),
                    row.get('last_updated', None),
                    row.get('source_document', None)
                ))
            
            # Insert products with the new schema
            execute_values(
                cur,
                """
                INSERT INTO products 
                (name, price, unit_price, category, market_id, image_url, description, 
                availability, regular_price, discounted_price, discount_percent, 
                discount_type, discount_period, last_updated, source_document)
                VALUES %s
                """,
                product_data
            )
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error storing products: {e}")
        return False

def get_products_from_db():
    """
    Retrieves all products from the database.
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing product data joined with market data.
    """
    try:
        conn = get_db_connection()
        
        # Query to join products and markets with all KAM fields
        query = """
            SELECT 
                p.id, p.name, p.price, p.unit_price, p.category, 
                m.name as market, p.image_url, p.description, 
                p.availability, p.regular_price, p.discounted_price, 
                p.discount_percent, p.discount_type, p.discount_period,
                p.last_updated, p.source_document
            FROM 
                products p
            JOIN 
                markets m ON p.market_id = m.id
        """
        
        # Read the data into a DataFrame
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error retrieving products: {e}")
        return pd.DataFrame()