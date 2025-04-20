import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar, Doughnut } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';

// Register Chart.js components
Chart.register(...registerables);

const MarketAnalysis = () => {
  const [markets, setMarkets] = useState([]);
  const [marketData, setMarketData] = useState({});
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('/api/market-analysis');
        setMarketData(response.data.marketData);
        setMarkets(response.data.markets);
        setCategories(response.data.categories);
        setLoading(false);
      } catch (error) {
        setError('Error loading market analysis data');
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  const getPriceComparisonData = () => {
    if (!marketData.averagePrices) return null;
    
    let prices = { ...marketData.averagePrices };
    
    // Filter by category if selected
    if (selectedCategory) {
      prices = Object.keys(prices).reduce((filtered, market) => {
        filtered[market] = prices[market][selectedCategory] || 0;
        return filtered;
      }, {});
    } else {
      // If no category selected, use overall average
      prices = Object.keys(prices).reduce((filtered, market) => {
        const categoryValues = Object.values(prices[market]);
        filtered[market] = categoryValues.length > 0 
          ? categoryValues.reduce((sum, price) => sum + price, 0) / categoryValues.length 
          : 0;
        return filtered;
      }, {});
    }
    
    return {
      labels: Object.keys(prices),
      datasets: [
        {
          label: selectedCategory || 'Overall Average',
          data: Object.values(prices),
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }
      ]
    };
  };
  
  const getProductDistributionData = () => {
    if (!marketData.productDistribution) return null;
    
    return {
      labels: Object.keys(marketData.productDistribution),
      datasets: [
        {
          data: Object.values(marketData.productDistribution),
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)',
            'rgba(255, 159, 64, 0.5)',
            'rgba(199, 199, 199, 0.5)',
            'rgba(83, 102, 255, 0.5)',
            'rgba(40, 159, 64, 0.5)',
            'rgba(210, 199, 199, 0.5)',
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(199, 199, 199, 1)',
            'rgba(83, 102, 255, 1)',
            'rgba(40, 159, 64, 1)',
            'rgba(210, 199, 199, 1)',
          ],
          borderWidth: 1
        }
      ]
    };
  };
  
  const getCategoryDistributionData = () => {
    if (!marketData.categoryDistribution) return null;
    
    return {
      labels: Object.keys(marketData.categoryDistribution),
      datasets: [
        {
          data: Object.values(marketData.categoryDistribution),
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)',
            'rgba(255, 159, 64, 0.5)',
            'rgba(199, 199, 199, 0.5)',
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(199, 199, 199, 1)',
          ],
          borderWidth: 1
        }
      ]
    };
  };
  
  const barOptions = {
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Average Price ($)'
        }
      }
    },
    plugins: {
      title: {
        display: true,
        text: `Average Prices by Market ${selectedCategory ? '- ' + selectedCategory : ''}`,
        font: {
          size: 16
        }
      }
    },
    maintainAspectRatio: false
  };
  
  const doughnutOptions = {
    plugins: {
      legend: {
        position: 'right'
      }
    },
    maintainAspectRatio: false
  };
  
  if (loading) {
    return <div className="card">Loading market analysis data...</div>;
  }
  
  if (error) {
    return <div className="card alert alert-danger">{error}</div>;
  }
  
  return (
    <div>
      <div className="card">
        <h2>Market Analysis</h2>
        <p>Analyze and compare market data</p>
        
        <div className="form-group">
          <label htmlFor="categoryFilter">Filter by Category:</label>
          <select
            id="categoryFilter"
            className="form-control"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            style={{ maxWidth: '300px' }}
          >
            <option value="">All Categories</option>
            {categories.map((category, index) => (
              <option key={index} value={category}>{category}</option>
            ))}
          </select>
        </div>
      </div>
      
      <div className="card" style={{ marginTop: '20px' }}>
        <h3>Average Price Comparison</h3>
        <div className="chart-container">
          {getPriceComparisonData() ? (
            <Bar data={getPriceComparisonData()} options={barOptions} />
          ) : (
            <p>No price data available for the selected category.</p>
          )}
        </div>
      </div>
      
      <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
        <div className="card" style={{ flex: 1 }}>
          <h3>Product Distribution by Market</h3>
          <div className="chart-container">
            {getProductDistributionData() ? (
              <Doughnut data={getProductDistributionData()} options={doughnutOptions} />
            ) : (
              <p>No product distribution data available.</p>
            )}
          </div>
        </div>
        
        <div className="card" style={{ flex: 1 }}>
          <h3>Category Distribution</h3>
          <div className="chart-container">
            {getCategoryDistributionData() ? (
              <Doughnut data={getCategoryDistributionData()} options={doughnutOptions} />
            ) : (
              <p>No category distribution data available.</p>
            )}
          </div>
        </div>
      </div>
      
      <div className="card" style={{ marginTop: '20px' }}>
        <h3>Market Insights</h3>
        <div>
          {marketData.insights ? (
            <ul>
              {marketData.insights.map((insight, index) => (
                <li key={index}>{insight}</li>
              ))}
            </ul>
          ) : (
            <p>No market insights available.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default MarketAnalysis;