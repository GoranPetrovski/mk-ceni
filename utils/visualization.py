import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_price_comparison_chart(data):
    """
    Create a bar chart comparing prices for a product across different markets.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing price data for a single product across markets
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Interactive price comparison chart
    """
    # Sort data by price
    sorted_data = data.sort_values('price')
    
    # Create color scale - lighter colors for higher prices
    colors = px.colors.sequential.Reds_r[:len(sorted_data)]
    
    # Create the figure
    fig = go.Figure()
    
    # Add bars for each market
    for i, (_, row) in enumerate(sorted_data.iterrows()):
        fig.add_trace(go.Bar(
            x=[row['market']],
            y=[row['price']],
            name=row['market'],
            marker_color=colors[i % len(colors)],
            text=f"${row['price']:.2f}",
            textposition='auto',
        ))
    
    # Update layout
    fig.update_layout(
        title=f"Price Comparison for {sorted_data.iloc[0]['name']}",
        xaxis_title="Market",
        yaxis_title="Price ($)",
        height=400,
        margin=dict(l=40, r=40, t=60, b=40),
        yaxis=dict(
            tickprefix="$",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        bargap=0.3,
    )
    
    return fig

def create_market_comparison_chart(data):
    """
    Create a visualization comparing markets based on product prices.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing product data for multiple markets
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Interactive market comparison chart
    """
    # Calculate average price by market
    avg_prices = data.groupby('market')['price'].mean().reset_index()
    avg_prices = avg_prices.sort_values('price')
    
    # Calculate product count by market
    product_counts = data.groupby('market').size().reset_index(name='count')
    
    # Merge data
    market_data = pd.merge(avg_prices, product_counts, on='market')
    
    # Create the figure
    fig = px.bar(
        market_data,
        x='market',
        y='price',
        title="Average Price by Market",
        color='price',
        color_continuous_scale=px.colors.sequential.Reds_r,
        labels={'market': 'Market', 'price': 'Average Price ($)', 'count': 'Number of Products'},
        text=market_data['price'].apply(lambda x: f"${x:.2f}"),
        hover_data=['count'],
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        margin=dict(l=40, r=40, t=60, b=40),
        yaxis=dict(
            tickprefix="$",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
    )
    
    fig.update_traces(textposition='auto')
    
    return fig

def create_price_distribution_chart(data, category=None):
    """
    Create a histogram showing price distribution.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing product data
    category : str, optional
        Category to filter by
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Interactive price distribution chart
    """
    # Filter by category if specified
    if category:
        filtered_data = data[data['category'] == category]
        title = f"Price Distribution for {category} Products"
    else:
        filtered_data = data
        title = "Price Distribution for All Products"
    
    # Create histogram
    fig = px.histogram(
        filtered_data,
        x='price',
        color='market',
        title=title,
        labels={'price': 'Price ($)', 'count': 'Number of Products', 'market': 'Market'},
        opacity=0.8,
        barmode='overlay',
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(
            tickprefix="$",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        bargap=0.1,
    )
    
    return fig

def create_category_comparison_chart(data):
    """
    Create a chart comparing average prices across product categories.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing product data with categories
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Interactive category comparison chart
    """
    # Ensure category column exists
    if 'category' not in data.columns:
        # Create a dummy chart with a message
        fig = go.Figure()
        fig.add_annotation(
            text="No category data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Calculate average price by category
    avg_prices = data.groupby('category')['price'].mean().reset_index()
    
    # Calculate product count by category
    product_counts = data.groupby('category').size().reset_index(name='count')
    
    # Merge data
    category_data = pd.merge(avg_prices, product_counts, on='category')
    
    # Sort by average price
    category_data = category_data.sort_values('price', ascending=False)
    
    # Create the figure
    fig = px.bar(
        category_data,
        y='category',
        x='price',
        title="Average Price by Category",
        color='price',
        color_continuous_scale=px.colors.sequential.Reds_r,
        labels={'category': 'Category', 'price': 'Average Price ($)', 'count': 'Number of Products'},
        text=category_data['price'].apply(lambda x: f"${x:.2f}"),
        hover_data=['count'],
        orientation='h',
    )
    
    # Update layout
    fig.update_layout(
        height=500,
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(
            tickprefix="$",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
    )
    
    fig.update_traces(textposition='auto')
    
    return fig