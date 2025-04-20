package com.pricecomparison.services;

import com.pricecomparison.models.Product;
import com.pricecomparison.repositories.ProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class ProductService {

    private final ProductRepository productRepository;
    
    /**
     * Get all products
     * @return List of all products
     */
    public List<Product> getAllProducts() {
        return productRepository.findAll();
    }
    
    /**
     * Get product by ID
     * @param id Product ID
     * @return Optional containing the product if found
     */
    public Optional<Product> getProductById(Long id) {
        return productRepository.findById(id);
    }
    
    /**
     * Search products by name
     * @param query Search query
     * @return List of matching products
     */
    public List<Product> searchProducts(String query) {
        if (query == null || query.trim().isEmpty()) {
            return Collections.emptyList();
        }
        return productRepository.findByNameContainingIgnoreCase(query.trim());
    }
    
    /**
     * Filter products based on criteria
     * @param category Category filter
     * @param minPrice Minimum price filter
     * @param maxPrice Maximum price filter
     * @return List of filtered products
     */
    public List<Product> filterProducts(String category, Double minPrice, Double maxPrice) {
        return productRepository.findByFilters(
            category != null && !category.trim().isEmpty() ? category : null,
            minPrice,
            maxPrice
        );
    }
    
    /**
     * Get all product categories
     * @return List of unique categories
     */
    public List<String> getAllCategories() {
        return productRepository.findAllCategories();
    }
    
    /**
     * Get all markets that have products
     * @return List of market names
     */
    public List<String> getAllMarkets() {
        return productRepository.findAllMarkets();
    }
    
    /**
     * Save a single product
     * @param product Product to save
     * @return Saved product
     */
    @Transactional
    public Product save(Product product) {
        return productRepository.save(product);
    }
    
    /**
     * Save multiple products
     * @param products List of products to save
     * @return List of saved products
     */
    @Transactional
    public List<Product> saveAll(List<Product> products) {
        return productRepository.saveAll(products);
    }
    
    /**
     * Delete a product
     * @param id Product ID
     */
    @Transactional
    public void deleteProduct(Long id) {
        productRepository.deleteById(id);
    }
    
    /**
     * Remove duplicate products
     * This method finds products with the same name and market, and keeps the one with the most recent price
     */
    @Transactional
    public int removeDuplicates() {
        int removedCount = 0;
        List<String> markets = getAllMarkets();
        
        for (String market : markets) {
            List<Product> marketProducts = productRepository.findByMarket(market);
            
            // Group by product name
            java.util.Map<String, List<Product>> productsByName = new java.util.HashMap<>();
            
            for (Product product : marketProducts) {
                productsByName.computeIfAbsent(product.getName().toLowerCase(), k -> new java.util.ArrayList<>())
                        .add(product);
            }
            
            // For each group with more than one product, keep only the most recent one
            for (List<Product> duplicates : productsByName.values()) {
                if (duplicates.size() > 1) {
                    // Sort by updated timestamp descending
                    duplicates.sort((p1, p2) -> p2.getUpdatedAt().compareTo(p1.getUpdatedAt()));
                    
                    // Keep the first one (most recent), delete the rest
                    for (int i = 1; i < duplicates.size(); i++) {
                        productRepository.delete(duplicates.get(i));
                        removedCount++;
                    }
                }
            }
        }
        
        return removedCount;
    }
}