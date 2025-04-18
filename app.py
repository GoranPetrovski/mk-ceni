import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.pdf_extractor import extract_prices_from_pdf
from utils.data_processor import process_data, filter_data, search_products
from utils.visualization import create_price_comparison_chart, create_market_comparison_chart, create_price_distribution_chart
import os
import tempfile

# Set page configuration
st.set_page_config(
    page_title="Price Comparison Tool",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data' not in st.session_state:
    # Load sample data if available
    try:
        sample_data = pd.read_csv('data/sample_data.csv')
        st.session_state.data = sample_data
    except:
        st.session_state.data = None
        
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = st.session_state.data

# Apply custom CSS - directly embedded to avoid file reading issues
st.markdown("""
<style>
/* Cenoteka-styled Product Cards */
.cenoteka-product-card {
    display: flex;
    flex-direction: column;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    height: 100%;
    position: relative;
}

.cenoteka-product-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.cenoteka-product-card img {
    width: 100%;
    height: 180px;
    object-fit: contain;
    background-color: #f8f9fa;
    padding: 10px;
}

.cenoteka-product-card .card-body {
    padding: 15px;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}

.cenoteka-product-card .card-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #333;
    line-height: 1.3;
    height: 42px;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.cenoteka-product-card .card-category {
    font-size: 12px;
    color: #6c757d;
    margin-bottom: 8px;
}

.cenoteka-product-card .card-price {
    font-size: 18px;
    font-weight: bold;
    color: #e63946;
    margin-top: auto;
}

.cenoteka-product-card .card-original-price {
    font-size: 14px;
    color: #6c757d;
    text-decoration: line-through;
    margin-right: 8px;
}

.cenoteka-product-card .card-discount {
    position: absolute;
    top: 10px;
    right: 10px;
    background-color: #e63946;
    color: white;
    font-size: 14px;
    font-weight: bold;
    padding: 4px 8px;
    border-radius: 4px;
}

.cenoteka-product-card .card-market {
    font-size: 12px;
    color: #457b9d;
    margin-top: 8px;
    display: block;
}

.cenoteka-product-card .card-unit-price {
    font-size: 12px;
    color: #6c757d;
    margin-top: 4px;
}

.cenoteka-product-card .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px;
    background-color: #f8f9fa;
    border-top: 1px solid #e9ecef;
}

.cenoteka-product-card .card-compare {
    background-color: #457b9d;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 12px;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.cenoteka-product-card .card-compare:hover {
    background-color: #1d3557;
}

/* Grid Layout for Products */
.cenoteka-product-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

/* Filter and Search Section */
.cenoteka-filter-section {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    padding: 20px;
    margin-bottom: 20px;
}

/* Modify Streamlit elements to match Cenoteka style */
div.stButton > button {
    background-color: #e63946;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: 600;
}

div.stButton > button:hover {
    background-color: #c1121f;
}

/* Section Headers */
.section-header {
    color: #1d3557;
    font-size: 24px;
    font-weight: 700;
    margin-top: 30px;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e63946;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: #f8f9fa;
    border-radius: 4px 4px 0 0;
    border: 1px solid #e9ecef;
    border-bottom: none;
    color: #1d3557;
}

.stTabs [aria-selected="true"] {
    background-color: white;
    border-top: 3px solid #e63946;
}

/* Product count badge */
.product-count-badge {
    display: inline-block;
    background-color: #457b9d;
    color: white;
    font-size: 12px;
    padding: 3px 8px;
    border-radius: 12px;
    margin-left: 8px;
}

/* Price range slider */
div.stSlider [data-baseweb="slider"] {
    height: 6px;
}

div.stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
    background-color: #e63946;
    border-color: #e63946;
}

/* Comparison chart styling */
.comparison-chart {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    padding: 20px;
    margin-top: 20px;
}

/* Empty state */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 50px;
    background-color: #f8f9fa;
    border-radius: 8px;
    text-align: center;
}

.empty-state img {
    max-width: 150px;
    margin-bottom: 20px;
    opacity: 0.7;
}

.empty-state h3 {
    color: #1d3557;
    margin-bottom: 10px;
}

.empty-state p {
    color: #6c757d;
    max-width: 400px;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Data Extraction", "Web Scraping", "Price Comparison", "Market Analysis"])

# Import the web scraper and database modules
from utils.web_scraper import scrape_stokomak_prices, scrape_vero_prices
from utils.database import setup_database, store_scraped_products, get_products_from_db
from utils.kam_extractor import extract_kam_prices_from_pdf, kam_pdf_to_csv
from utils.sample_data import load_sample_data
import base64
import random
from PIL import Image
import io

# Function to get default image if none is available
def get_default_image(category=None):
    # Default placeholder image for products
    if category and category.lower() in ['fruits', 'vegetables', 'produce']:
        return "https://cdn-icons-png.flaticon.com/512/3194/3194766.png"
    elif category and category.lower() in ['meat', 'poultry', 'fish']:
        return "https://cdn-icons-png.flaticon.com/512/3075/3075977.png"
    elif category and category.lower() in ['dairy', 'milk', 'cheese']:
        return "https://cdn-icons-png.flaticon.com/512/2674/2674486.png"
    elif category and category.lower() in ['bakery', 'bread', 'pastries']:
        return "https://cdn-icons-png.flaticon.com/512/5787/5787086.png"
    else:
        return "https://cdn-icons-png.flaticon.com/512/3724/3724763.png"

# Function to create a product card in HTML
def create_product_card(product):
    name = product.get('name', 'Unknown Product')
    price = product.get('price', 0)
    market = product.get('market', 'Unknown Store')
    category = product.get('category', '')
    regular_price = product.get('regular_price', None)
    discounted_price = product.get('discounted_price', None)
    unit_price = product.get('unit_price', None)
    discount_percent = product.get('discount_percent', None)
    
    # Get image URL based on product category
    image_url = get_default_image(category)
    
    # Create discount badge if there's a discount
    discount_badge = ""
    if discount_percent and discount_percent > 0:
        discount_badge = f'<div class="card-discount">-{int(discount_percent)}%</div>'
    
    # Create pricing section
    price_html = f'<div class="card-price">{price} MKD</div>'
    if regular_price and regular_price > price:
        price_html = f'<span class="card-original-price">{regular_price} MKD</span>{price_html}'
    
    # Create unit price if available
    unit_price_html = ""
    if unit_price:
        unit_price_html = f'<div class="card-unit-price">{unit_price}</div>'
    
    # Final card HTML
    card_html = f"""
    <div class="cenoteka-product-card">
        {discount_badge}
        <img src="{image_url}" alt="{name}">
        <div class="card-body">
            <div class="card-title">{name}</div>
            <div class="card-category">{category}</div>
            {price_html}
            {unit_price_html}
            <span class="card-market">📍 {market}</span>
        </div>
        <div class="card-footer">
            <button class="card-compare">Compare Prices</button>
        </div>
    </div>
    """
    return card_html

# Home Page
if page == "Home":
    # App title
    st.title("MK Price Comparison")
    st.write("Find the best prices for products across different markets in Macedonia")
    
    # Check if we have data
    if st.session_state.data is None or st.session_state.data.empty:
        # Load from database if available
        try:
            db_products = get_products_from_db()
            if not db_products.empty:
                st.session_state.data = db_products
                st.session_state.filtered_data = db_products
        except Exception as e:
            st.error(f"Could not load data from database: {e}")
    
    # Search and filter section
    st.markdown('<div class="section-header">Find Products</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input("Search Products", placeholder="Search by name...")
    
    with col2:
        if st.session_state.data is not None and not st.session_state.data.empty:
            categories = st.session_state.data['category'].dropna().unique()
            selected_category = st.selectbox("Category", ["All Categories"] + list(categories))
        else:
            selected_category = "All Categories"
    
    with col3:
        if st.session_state.data is not None and not st.session_state.data.empty:
            markets = st.session_state.data['market'].unique()
            selected_market = st.selectbox("Market", ["All Markets"] + list(markets))
        else:
            selected_market = "All Markets"
    
    # Display products in a grid layout
    if st.session_state.data is not None and not st.session_state.data.empty:
        # Filter data based on selections
        data = st.session_state.data
        
        if search_query:
            data = search_products(data, search_query)
        
        if selected_category != "All Categories":
            data = data[data['category'] == selected_category]
        
        if selected_market != "All Markets":
            data = data[data['market'] == selected_market]
        
        # Display product count
        product_count = len(data)
        st.markdown(f'<div class="section-header">Products <span class="product-count-badge">{product_count}</span></div>', unsafe_allow_html=True)
        
        if product_count == 0:
            st.markdown("""
            <div class="empty-state">
                <img src="https://cdn-icons-png.flaticon.com/512/1178/1178479.png" alt="No results">
                <h3>No products found</h3>
                <p>Try adjusting your search or filters to find what you're looking for.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Prepare the grid of product cards
            grid_html = '<div class="cenoteka-product-grid">'
            
            # Loop through products and create cards
            for _, product in data.iterrows():
                grid_html += create_product_card(product)
            
            grid_html += '</div>'
            
            # Display the product grid
            st.markdown(grid_html, unsafe_allow_html=True)
            
            # Show a "Load More" button if there are many products
            if product_count > 20:
                st.button("Load More Products")
    else:
        # Empty state
        st.markdown("""
        <div class="empty-state">
            <img src="https://cdn-icons-png.flaticon.com/512/7518/7518748.png" alt="No data">
            <h3>No products available</h3>
            <p>Add products by extracting data from PDF price lists or by scraping websites in the Web Scraping page.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick action buttons for empty state
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Extract from PDF"):
                st.session_state.nav_page = "Data Extraction"
                st.rerun()
        with col2:
            if st.button("Scrape Websites"):
                st.session_state.nav_page = "Web Scraping"
                st.rerun()
        with col3:
            if st.button("Load Sample Data"):
                with st.spinner("Loading sample product data..."):
                    sample_data = load_sample_data()
                    st.session_state.data = sample_data
                    st.session_state.filtered_data = sample_data
                    st.success("Loaded sample data successfully!")
                    st.rerun()

# App title for other pages
elif page != "Home":
    st.title("Price Comparison Tool")
    st.write("Compare product prices across different markets")

# Data Extraction Page
if page == "Data Extraction":
    st.header("Data Extraction")
    st.write("Upload PDF files containing product prices")
    
    # Add tabs for different extraction methods
    extraction_tab = st.radio("Extraction Method", ["Generic PDF Extraction", "KAM Price List"])
    
    if extraction_tab == "Generic PDF Extraction":
        uploaded_files = st.file_uploader("Choose PDF files", accept_multiple_files=True, type="pdf", key="generic_pdfs")
    
    elif extraction_tab == "KAM Price List":
        st.write("Upload KAM price list PDF file")
        uploaded_files = st.file_uploader("Choose KAM PDF file", accept_multiple_files=False, type="pdf", key="kam_pdf")
        
        if uploaded_files:
            if st.button("Extract KAM Prices"):
                with st.spinner("Extracting prices from KAM PDF..."):
                    # Save the uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_files.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Extract KAM data
                    kam_data = extract_kam_prices_from_pdf(tmp_path)
                    
                    # Create CSV file
                    csv_path = "data/kam_prices.csv"
                    kam_pdf_to_csv(tmp_path, csv_path)
                    
                    # Clean up the temporary file
                    os.unlink(tmp_path)
                    
                    if kam_data is not None and not kam_data.empty:
                        # Store in database
                        setup_database()
                        store_result = store_scraped_products(kam_data)
                        
                        if store_result:
                            st.success(f"Successfully extracted and stored {len(kam_data)} products from KAM price list!")
                        else:
                            st.error("Failed to store products in the database.")
                        
                        # Update session state
                        st.session_state.data = kam_data
                        st.session_state.filtered_data = kam_data
                        
                        # Display the extracted data
                        st.write("**Extracted KAM Products:**")
                        st.dataframe(kam_data)
                        
                        # Option to download as CSV
                        csv = kam_data.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "Download CSV",
                            csv,
                            "kam_prices.csv",
                            "text/csv",
                            key='download-kam-csv'
                        )
                    else:
                        st.error("Could not extract data from KAM price list.")
        
        # Instructions for KAM price list
        with st.expander("KAM Price List Instructions"):
            st.write("""
            1. Upload the KAM price list PDF file.
            2. Click "Extract KAM Prices" to process the file.
            3. The system will automatically extract product details including:
               - Product name
               - Price
               - Unit price (per 100g/ml)
               - Product description
               - Regular and discounted prices
               - Availability information
            4. The extracted data will be saved to the database and can be used in the Price Comparison page.
            """)
    
    # Generic PDF extraction method
    if extraction_tab == "Generic PDF Extraction":
        if uploaded_files and st.button("Extract Prices"):
            extracted_data_list = []
            
            with st.spinner("Extracting data from PDFs..."):
                for uploaded_file in uploaded_files:
                    # Save the uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Extract data from the PDF
                    extracted_data = extract_prices_from_pdf(tmp_path)
                    
                    # Clean up the temporary file
                    os.unlink(tmp_path)
                    
                    if extracted_data is not None and not extracted_data.empty:
                        market_name = os.path.splitext(uploaded_file.name)[0]  # Use filename without extension as market name
                        extracted_data['market'] = extracted_data.get('market', market_name)
                        extracted_data_list.append(extracted_data)
                        st.success(f"Successfully extracted data from {uploaded_file.name}")
                    else:
                        st.error(f"Could not extract data from {uploaded_file.name}")
            
            if extracted_data_list:
                # Process and combine the extracted data
                st.session_state.data = process_data(extracted_data_list)
                st.session_state.filtered_data = st.session_state.data
                
                # Display the extracted data
                st.write(f"**Extracted {len(st.session_state.data)} products**")
                st.dataframe(st.session_state.data)
                
                # Option to save to CSV
                csv = st.session_state.data.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download CSV",
                    csv,
                    "price_data.csv",
                    "text/csv",
                    key='download-csv'
                )
    
    # Instructions
    with st.expander("Instructions"):
        st.write("""
        1. Upload PDF files containing product prices.
        2. The system will automatically extract product names and prices.
        3. The market will be determined based on the PDF content or filename.
        4. Products will be categorized when possible.
        5. You can download the extracted data as a CSV file.
        """)

# Price Comparison Page
elif page == "Price Comparison":
    st.header("Price Comparison")
    st.write("Compare prices for products across different markets")
    
    if st.session_state.data is None:
        st.warning("No data available. Please extract data from PDFs in the Data Extraction page.")
    else:
        # Filters
        st.subheader("Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_query = st.text_input("Search Products", "")
        
        with col2:
            categories = st.session_state.data['category'].dropna().unique()
            selected_category = st.selectbox("Category", ["All"] + list(categories))
        
        with col3:
            markets = st.session_state.data['market'].unique()
            selected_markets = st.multiselect("Markets", options=markets, default=list(markets))
        
        col4, col5 = st.columns(2)
        
        with col4:
            min_price = st.number_input("Min Price", min_value=0.0, value=0.0, step=1.0)
        
        with col5:
            max_price = st.number_input("Max Price", min_value=0.0, value=1000.0, step=1.0)
        
        # Apply filters
        data = st.session_state.data
        
        # Filter by search query
        if search_query:
            data = search_products(data, search_query)
        
        # Filter by category, price range, and markets
        category_filter = None if selected_category == "All" else selected_category
        data = filter_data(data, category=category_filter, min_price=min_price, max_price=max_price, markets=selected_markets)
        
        st.session_state.filtered_data = data
        
        # Display filtered data
        if data.empty:
            st.warning("No products match your filters.")
        else:
            st.subheader("Product List")
            st.dataframe(data)
            
            # Product comparison
            st.subheader("Price Comparison")
            
            # Get unique product names
            product_names = data['name'].unique()
            
            if len(product_names) > 0:
                selected_product = st.selectbox("Select a product to compare", product_names)
                
                # Get data for the selected product across markets
                product_data = data[data['name'] == selected_product]
                
                if len(product_data) > 1:
                    # Create comparison chart
                    fig = create_price_comparison_chart(product_data)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("This product is only available in one market.")
                    st.dataframe(product_data[['name', 'price', 'market']])
            else:
                st.info("No products available to compare.")

# Web Scraping Page
elif page == "Web Scraping":
    st.header("Web Scraping")
    st.write("Scrape product prices from websites")
    
    # Add sections for different stores
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Stokomak Products")
        st.write("Scrape product prices from stokomak.com.mk")
    
    with col2:
        st.subheader("Vero Products")
        st.write("Scrape product prices from Vero's price list")
        
        if st.button("Scrape Vero Prices"):
            with st.spinner("Scraping products from Vero..."):
                setup_result = setup_database()
                
                if not setup_result:
                    st.error("Failed to set up database. Please check your database connection.")
                else:
                    scraped_products = scrape_vero_prices()
                    
                    if scraped_products is None or scraped_products.empty:
                        st.error("Could not scrape products from Vero. Please try again later.")
                    else:
                        storage_result = store_scraped_products(scraped_products)
                        
                        if not storage_result:
                            st.error("Failed to store products in the database.")
                        else:
                            st.success(f"Successfully scraped and stored {len(scraped_products)} products from Vero")
                            st.dataframe(scraped_products)
                            
                            csv = scraped_products.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "Download Scraped Data as CSV",
                                csv,
                                "vero_prices.csv",
                                "text/csv",
                                key='download-vero-csv'
                            )
    
    # Create a button to start scraping
    if st.button("Scrape Stokomak Prices"):
        # Show a spinner while scraping
        with st.spinner("Scraping products from Stokomak..."):
            # Create the database tables if they don't exist
            setup_result = setup_database()
            
            if not setup_result:
                st.error("Failed to set up database. Please check your database connection.")
            else:
                # Scrape the products
                scraped_products = scrape_stokomak_prices()
                
                if scraped_products is None or scraped_products.empty:
                    st.error("Could not scrape products from Stokomak. Please try again later.")
                else:
                    # Store the scraped products in the database
                    storage_result = store_scraped_products(scraped_products)
                    
                    if not storage_result:
                        st.error("Failed to store products in the database.")
                    else:
                        st.success(f"Successfully scraped and stored {len(scraped_products)} products from Stokomak!")
                        
                        # Display the scraped data
                        st.write("**Scraped Products:**")
                        st.dataframe(scraped_products)
                        
                        # Update the session state with the combined data (previous data + new data)
                        db_products = get_products_from_db()
                        if not db_products.empty:
                            st.session_state.data = db_products
                            st.session_state.filtered_data = db_products
                        
                        # Option to save to CSV
                        csv = scraped_products.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "Download Scraped Data as CSV",
                            csv,
                            "stokomak_prices.csv",
                            "text/csv",
                            key='download-scraped-csv'
                        )
    
    # Add instructions for the web scraping feature
    with st.expander("Instructions"):
        st.write("""
        1. Click the "Scrape Stokomak Prices" button to start the scraping process.
        2. The system will connect to stokomak.com.mk and extract product prices.
        3. The scraped data will be automatically saved to the database.
        4. The product data will become available in the Price Comparison and Market Analysis pages.
        5. You can download the scraped data as a CSV file.
        """)
    
    # Section to load data from database
    st.subheader("Database Products")
    if st.button("Load Products from Database"):
        with st.spinner("Loading products from database..."):
            db_products = get_products_from_db()
            
            if db_products.empty:
                st.warning("No products found in the database.")
            else:
                st.success(f"Successfully loaded {len(db_products)} products from the database!")
                st.session_state.data = db_products
                st.session_state.filtered_data = db_products
                
                # Display the loaded data
                st.write("**Database Products:**")
                st.dataframe(db_products)

# Market Analysis Page
elif page == "Market Analysis":
    st.header("Market Analysis")
    st.write("Analyze and compare market data")
    
    if st.session_state.data is None:
        st.warning("No data available. Please extract data from PDFs in the Data Extraction page.")
    else:
        # Filters for analysis
        categories = st.session_state.data['category'].dropna().unique()
        selected_category = st.selectbox("Filter by Category", ["All"] + list(categories))
        
        # Filter data by category if selected
        if selected_category == "All":
            data = st.session_state.data
        else:
            data = st.session_state.data[st.session_state.data['category'] == selected_category]
        
        if data.empty:
            st.warning("No data available for the selected category.")
        else:
            # Market price comparison
            st.subheader("Average Price Comparison")
            fig_market = create_market_comparison_chart(data)
            st.plotly_chart(fig_market, use_container_width=True)
            
            # Product distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Product Distribution by Market")
                market_counts = data['market'].value_counts()
                fig_pie = px.pie(
                    names=market_counts.index,
                    values=market_counts.values,
                    title="Number of Products by Market"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.subheader("Price Distribution")
                fig_hist = create_price_distribution_chart(data, selected_category if selected_category != "All" else None)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # Market insights
            st.subheader("Market Insights")
            
            # Calculate and display market with lowest average prices
            market_avg_prices = data.groupby('market')['price'].mean().reset_index()
            cheapest_market = market_avg_prices.loc[market_avg_prices['price'].idxmin()]
            
            st.write(f"✅ **{cheapest_market['market']}** offers the lowest average prices overall.")
            
            # Calculate price variation
            markets = data['market'].unique()
            if len(markets) > 1:
                # Find products available in multiple markets
                product_counts = data.groupby('name')['market'].nunique()
                multi_market_products = product_counts[product_counts > 1].index
                
                if len(multi_market_products) > 0:
                    # Calculate price variations for multi-market products
                    price_variations = []
                    
                    for product in multi_market_products:
                        product_data = data[data['name'] == product]
                        max_price = product_data['price'].max()
                        min_price = product_data['price'].min()
                        variation = (max_price - min_price) / min_price * 100
                        price_variations.append({
                            'product': product,
                            'variation': variation,
                            'max_price': max_price,
                            'min_price': min_price
                        })
                    
                    # Sort by price variation and get top 3
                    price_variations = sorted(price_variations, key=lambda x: x['variation'], reverse=True)[:3]
                    
                    st.write("**Products with highest price variations:**")
                    for item in price_variations:
                        st.write(f"- **{item['product']}**: {item['variation']:.1f}% variation (${item['min_price']:.2f} to ${item['max_price']:.2f})")
            
            # Display product count by market
            st.write("**Product counts by market:**")
            for market, count in market_counts.items():
                st.write(f"- **{market}**: {count} products")