package com.pricecomparison.repositories;

import com.pricecomparison.models.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    List<Product> findByNameContainingIgnoreCase(String name);
    
    List<Product> findByCategory(String category);
    
    List<Product> findByMarket(String market);
    
    @Query("SELECT p FROM Product p WHERE (:category IS NULL OR p.category = :category) " +
           "AND (:minPrice IS NULL OR p.price >= :minPrice) " +
           "AND (:maxPrice IS NULL OR p.price <= :maxPrice)")
    List<Product> findByFilters(
            @Param("category") String category,
            @Param("minPrice") Double minPrice,
            @Param("maxPrice") Double maxPrice);
            
    @Query("SELECT DISTINCT p.category FROM Product p WHERE p.category IS NOT NULL")
    List<String> findAllCategories();
    
    @Query("SELECT DISTINCT p.market FROM Product p")
    List<String> findAllMarkets();
    
    @Query("SELECT AVG(p.price) FROM Product p WHERE p.market = :market")
    Double findAveragePriceByMarket(@Param("market") String market);
    
    @Query("SELECT AVG(p.price) FROM Product p WHERE p.market = :market AND p.category = :category")
    Double findAveragePriceByMarketAndCategory(
            @Param("market") String market, 
            @Param("category") String category);
    
    @Query("SELECT COUNT(p) FROM Product p GROUP BY p.market")
    List<Long> countProductsByMarket();
    
    @Query("SELECT COUNT(p) FROM Product p WHERE p.market = :market")
    Long countProductsBySpecificMarket(@Param("market") String market);
    
    @Query("SELECT COUNT(p) FROM Product p GROUP BY p.category")
    List<Long> countProductsByCategory();
    
    @Query("SELECT COUNT(p) FROM Product p WHERE p.category = :category")
    Long countProductsBySpecificCategory(@Param("category") String category);
}