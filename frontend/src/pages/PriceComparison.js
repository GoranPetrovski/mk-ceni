import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';

// Register Chart.js components
Chart.register(...registerables);

const PriceComparison = () => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [markets, setMarkets] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    category: '',
    minPrice: '',
    maxPrice: '',
    markets: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('/api/products');
        setProducts(response.data);
        setFilteredProducts(response.data);
        
        // Extract unique categories and markets
        const uniqueCategories = [...new Set(response.data.map(p => p.category))].filter(Boolean);
        const uniqueMarkets = [...new Set(response.data.map(p => p.market))].filter(Boolean);
        
        setCategories(uniqueCategories);
        setMarkets(uniqueMarkets);
        setLoading(false);
      } catch (error) {
        setError('Error fetching product data');
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  useEffect(() => {
    applyFilters();
  }, [searchQuery, filters]);
  
  const applyFilters = () => {
    let filtered = [...products];
    
    // Apply search query
    if (searchQuery.trim() !== '') {
      filtered = filtered.filter(product => 
        product.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    // Apply category filter
    if (filters.category) {
      filtered = filtered.filter(product => product.category === filters.category);
    }
    
    // Apply price range filters
    if (filters.minPrice) {
      filtered = filtered.filter(product => product.price >= parseFloat(filters.minPrice));
    }
    
    if (filters.maxPrice) {
      filtered = filtered.filter(product => product.price <= parseFloat(filters.maxPrice));
    }
    
    // Apply market filters
    if (filters.markets.length > 0) {
      filtered = filtered.filter(product => filters.markets.includes(product.market));
    }
    
    setFilteredProducts(filtered);
  };
  
  const handleProductSelect = (product) => {
    setSelectedProduct(product);
  };
  
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters({
      ...filters,
      [name]: value
    });
  };
  
  const handleMarketChange = (market) => {
    const updatedMarkets = filters.markets.includes(market)
      ? filters.markets.filter(m => m !== market)
      : [...filters.markets, market];
    
    setFilters({
      ...filters,
      markets: updatedMarkets
    });
  };
  
  const resetFilters = () => {
    setFilters({
      category: '',
      minPrice: '',
      maxPrice: '',
      markets: []
    });
    setSearchQuery('');
  };
  
  const getChartData = () => {
    if (!selectedProduct) return null;
    
    // Find all instances of this product across different markets
    const productInstances = products.filter(
      p => p.name.toLowerCase() === selectedProduct.name.toLowerCase()
    );
    
    return {
      labels: productInstances.map(p => p.market),
      datasets: [
        {
          label: 'Price',
          data: productInstances.map(p => p.price),
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }
      ]
    };
  };
  
  const chartOptions = {
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Price ($)'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Market'
        }
      }
    },
    plugins: {
      title: {
        display: true,
        text: selectedProduct ? `Price Comparison for ${selectedProduct.name}` : '',
        font: {
          size: 16
        }
      },
      legend: {
        display: false
      }
    },
    maintainAspectRatio: false
  };
  
  if (loading) {
    return <div className="card">Loading product data...</div>;
  }
  
  if (error) {
    return <div className="card alert alert-danger">{error}</div>;
  }
  
  return (
    <div>
      <div className="card">
        <h2>Price Comparison</h2>
        <p>Compare prices for products across different markets</p>
        
        <div>
          <div className="form-group">
            <label htmlFor="searchQuery">Search Products:</label>
            <input
              type="text"
              id="searchQuery"
              className="form-control"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Enter product name"
            />
          </div>
          
          <div style={{ display: 'flex', gap: '15px', marginBottom: '15px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label htmlFor="category">Category:</label>
              <select
                id="category"
                name="category"
                className="form-control"
                value={filters.category}
                onChange={handleFilterChange}
              >
                <option value="">All Categories</option>
                {categories.map((category, index) => (
                  <option key={index} value={category}>{category}</option>
                ))}
              </select>
            </div>
            
            <div className="form-group" style={{ flex: 1 }}>
              <label htmlFor="minPrice">Min Price:</label>
              <input
                type="number"
                id="minPrice"
                name="minPrice"
                className="form-control"
                value={filters.minPrice}
                onChange={handleFilterChange}
                min="0"
                step="0.01"
              />
            </div>
            
            <div className="form-group" style={{ flex: 1 }}>
              <label htmlFor="maxPrice">Max Price:</label>
              <input
                type="number"
                id="maxPrice"
                name="maxPrice"
                className="form-control"
                value={filters.maxPrice}
                onChange={handleFilterChange}
                min="0"
                step="0.01"
              />
            </div>
          </div>
          
          <div className="form-group">
            <label>Markets:</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {markets.map((market, index) => (
                <div key={index} style={{ marginRight: '10px' }}>
                  <label style={{ display: 'flex', alignItems: 'center' }}>
                    <input
                      type="checkbox"
                      checked={filters.markets.includes(market)}
                      onChange={() => handleMarketChange(market)}
                      style={{ marginRight: '5px' }}
                    />
                    {market}
                  </label>
                </div>
              ))}
            </div>
          </div>
          
          <button className="btn" style={{ marginRight: '10px' }} onClick={applyFilters}>
            Apply Filters
          </button>
          <button className="btn btn-secondary" onClick={resetFilters}>
            Reset Filters
          </button>
        </div>
      </div>
      
      <div className="card" style={{ marginTop: '20px' }}>
        <h3>Product List</h3>
        {filteredProducts.length === 0 ? (
          <p>No products found matching your criteria.</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Product Name</th>
                  <th>Category</th>
                  <th>Market</th>
                  <th>Price</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.map((product, index) => (
                  <tr key={index}>
                    <td>{product.name}</td>
                    <td>{product.category || 'N/A'}</td>
                    <td>{product.market}</td>
                    <td>${product.price.toFixed(2)}</td>
                    <td>
                      <button 
                        className="btn" 
                        onClick={() => handleProductSelect(product)}
                      >
                        Compare
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      {selectedProduct && (
        <div className="card" style={{ marginTop: '20px' }}>
          <h3>Price Comparison</h3>
          <p>Comparing prices for {selectedProduct.name} across different markets</p>
          
          <div className="chart-container">
            <Bar data={getChartData()} options={chartOptions} />
          </div>
        </div>
      )}
    </div>
  );
};

export default PriceComparison;