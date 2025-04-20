package com.pricecomparison.repositories;

import com.pricecomparison.models.Market;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface MarketRepository extends JpaRepository<Market, Long> {
    
    Optional<Market> findByName(String name);
    
    boolean existsByName(String name);
}