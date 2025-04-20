import axios from 'axios';

const API_BASE_URL = '/api';

const apiService = {
  // Product endpoints
  getProducts: () => {
    return axios.get(`${API_BASE_URL}/products`);
  },
  
  getProductById: (id) => {
    return axios.get(`${API_BASE_URL}/products/${id}`);
  },
  
  searchProducts: (query) => {
    return axios.get(`${API_BASE_URL}/products/search`, { params: { query } });
  },
  
  filterProducts: (filters) => {
    return axios.get(`${API_BASE_URL}/products/filter`, { params: filters });
  },
  
  // PDF extraction endpoints
  extractPricesFromPdf: (formData) => {
    return axios.post(`${API_BASE_URL}/extract-prices`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  // Market analysis endpoints
  getMarketAnalysis: () => {
    return axios.get(`${API_BASE_URL}/market-analysis`);
  },
  
  getMarketAnalysisByCategory: (category) => {
    return axios.get(`${API_BASE_URL}/market-analysis/category/${category}`);
  },
  
  // Error handler
  handleError: (error) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response error:', error.response.data);
      return error.response.data.message || 'Error occurred in the server';
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Request error:', error.request);
      return 'No response from server. Please check your connection.';
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('General error:', error.message);
      return error.message;
    }
  }
};

export default apiService;