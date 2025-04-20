import React, { useState } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';

const DataExtraction = () => {
  const [files, setFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  
  const onDrop = acceptedFiles => {
    setFiles(prev => [...prev, ...acceptedFiles]);
  };
  
  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    }
  });
  
  const handleUpload = async () => {
    if (files.length === 0) {
      setUploadStatus({ type: 'error', message: 'Please select PDF files to upload' });
      return;
    }
    
    setIsUploading(true);
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    
    try {
      const response = await axios.post('/api/extract-prices', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setUploadStatus({ 
        type: 'success', 
        message: `Successfully extracted data from ${files.length} files. Found ${response.data.products} products.` 
      });
      setFiles([]);
    } catch (error) {
      setUploadStatus({ 
        type: 'error', 
        message: error.response?.data?.message || 'Error extracting data from PDF files' 
      });
    } finally {
      setIsUploading(false);
    }
  };
  
  const removeFile = (fileToRemove) => {
    setFiles(files.filter(file => file !== fileToRemove));
  };
  
  return (
    <div className="card">
      <h2>Data Extraction</h2>
      <p>Upload PDF files containing product prices</p>
      
      <div {...getRootProps({ className: 'dropzone' })}>
        <input {...getInputProps()} />
        <p>Drag 'n' drop PDF files here, or click to select files</p>
      </div>
      
      {files.length > 0 && (
        <div>
          <h3>Selected Files:</h3>
          <ul>
            {files.map((file, index) => (
              <li key={index}>
                {file.name} ({(file.size / 1024).toFixed(2)} KB)
                <button 
                  className="btn btn-secondary" 
                  style={{ marginLeft: '10px' }}
                  onClick={() => removeFile(file)}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
          <button 
            onClick={handleUpload} 
            disabled={isUploading} 
            className="btn"
          >
            {isUploading ? 'Uploading...' : 'Extract Prices'}
          </button>
        </div>
      )}
      
      {uploadStatus && (
        <div className={`alert alert-${uploadStatus.type === 'success' ? 'success' : 'danger'}`}>
          {uploadStatus.message}
        </div>
      )}
      
      <div className="card" style={{ marginTop: '20px' }}>
        <h3>Instructions</h3>
        <p>Upload PDF files containing product prices. The system will automatically:</p>
        <ul>
          <li>Extract product names and prices</li>
          <li>Determine the market based on the PDF content</li>
          <li>Categorize products when possible</li>
          <li>Store the data for price comparison</li>
        </ul>
        <p>Supported PDF formats include flyers, catalogs, and price lists.</p>
      </div>
    </div>
  );
};

export default DataExtraction;