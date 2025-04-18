import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, NavLink } from 'react-router-dom';
import DataExtraction from './pages/DataExtraction';
import PriceComparison from './pages/PriceComparison';
import MarketAnalysis from './pages/MarketAnalysis';
import './index.css';

function App() {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    // Handle search logic
    console.log('Searching for:', searchQuery);
  };

  return (
    <Router>
      <div className="app">
        {/* Header Navigation - Similar to Cenoteka */}
        <nav className="header-nav">
          <div className="header-nav-inner">
            <Link to="/" className="logo">CenoCompare</Link>
            <div className="main-nav">
              <ul>
                <li>
                  <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>
                    Home
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/extract" className={({ isActive }) => isActive ? 'active' : ''}>
                    Extract Data
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/compare" className={({ isActive }) => isActive ? 'active' : ''}>
                    Compare Prices
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/analysis" className={({ isActive }) => isActive ? 'active' : ''}>
                    Market Analysis
                  </NavLink>
                </li>
              </ul>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <div className="container">
          {/* Search Bar - Similar to Cenoteka */}
          <div className="search-container">
            <form onSubmit={handleSearchSubmit}>
              <input
                type="text"
                className="search-input"
                placeholder="Search for products..."
                value={searchQuery}
                onChange={handleSearchChange}
              />
              <span className="search-icon">🔍</span>
            </form>
          </div>

          {/* Routes */}
          <Routes>
            <Route path="/" element={
              <div>
                <div className="card">
                  <h2>Welcome to CenoCompare</h2>
                  <p>Compare product prices across different markets to find the best deals.</p>
                </div>
                
                <div className="card">
                  <h3>Featured Products</h3>
                  <div className="product-grid">
                    {/* Sample product cards - Will be replaced with real data */}
                    {[1, 2, 3, 4].map(index => (
                      <div className="product-card" key={index}>
                        <div className="product-card-image" style={{backgroundColor: '#f8f9fa', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                          <span style={{fontSize: '60px', color: '#ddd'}}>📱</span>
                        </div>
                        <div className="product-card-content">
                          <div className="product-card-name">Sample Product {index}</div>
                          <div className="product-card-price">${(19.99 * index).toFixed(2)}</div>
                          <div className="product-card-market">Market {index}</div>
                          <button className="compare-button">Compare Prices</button>
                        </div>
                        {index === 1 && <div className="product-card-badge">Best Deal</div>}
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="card">
                  <h3>Recent Price Comparisons</h3>
                  {/* Sample price bars - Will be replaced with real data */}
                  <div>
                    <div style={{marginBottom: '20px'}}>
                      <div className="product-card-name" style={{marginBottom: '10px'}}>Smartphone XYZ</div>
                      <div style={{display: 'flex', alignItems: 'center', marginBottom: '5px'}}>
                        <span className="price-bar-market">Market A</span>
                        <div className="price-bar" style={{width: '80%'}}>
                          <span className="price-bar-label">$499.99</span>
                        </div>
                      </div>
                      <div style={{display: 'flex', alignItems: 'center', marginBottom: '5px'}}>
                        <span className="price-bar-market">Market B</span>
                        <div className="price-bar" style={{width: '70%', backgroundColor: 'var(--secondary-color)'}}>
                          <span className="price-bar-label">$449.99</span>
                        </div>
                      </div>
                      <div style={{display: 'flex', alignItems: 'center'}}>
                        <span className="price-bar-market">Market C</span>
                        <div className="price-bar" style={{width: '60%', backgroundColor: 'var(--success-color)'}}>
                          <span className="price-bar-label">$399.99</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            } />
            <Route path="/extract" element={<DataExtraction />} />
            <Route path="/compare" element={<PriceComparison />} />
            <Route path="/analysis" element={<MarketAnalysis />} />
          </Routes>
        </div>

        {/* Footer */}
        <footer>
          <div className="container">
            <p>&copy; 2023 CenoCompare. All rights reserved.</p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;