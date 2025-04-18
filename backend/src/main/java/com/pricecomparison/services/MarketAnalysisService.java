package com.pricecomparison.services;

import com.pricecomparison.models.Product;
import com.pricecomparison.repositories.ProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class MarketAnalysisService {

    private final ProductRepository productRepository;
    
    /**
     * Get complete market analysis data
     * @return Map containing various market analysis metrics
     */
    public Map<String, Object> getMarketAnalysis() {
        Map<String, Object> result = new HashMap<>();
        
        List<String> markets = productRepository.findAllMarkets();
        List<String> categories = productRepository.findAllCategories();
        
        result.put("markets", markets);
        result.put("categories", categories);
        
        // Calculate average prices by market and category
        Map<String, Map<String, Double>> averagePrices = new HashMap<>();
        
        for (String market : markets) {
            Map<String, Double> marketPrices = new HashMap<>();
            
            // Overall average
            Double overallAvg = productRepository.findAveragePriceByMarket(market);
            if (overallAvg != null) {
                marketPrices.put("overall", overallAvg);
            }
            
            // Average by category
            for (String category : categories) {
                Double categoryAvg = productRepository.findAveragePriceByMarketAndCategory(market, category);
                if (categoryAvg != null) {
                    marketPrices.put(category, categoryAvg);
                }
            }
            
            averagePrices.put(market, marketPrices);
        }
        
        result.put("averagePrices", averagePrices);
        
        // Calculate product distribution by market
        Map<String, Long> productDistribution = new HashMap<>();
        for (String market : markets) {
            Long count = productRepository.countProductsBySpecificMarket(market);
            productDistribution.put(market, count);
        }
        
        result.put("productDistribution", productDistribution);
        
        // Calculate category distribution
        Map<String, Long> categoryDistribution = new HashMap<>();
        for (String category : categories) {
            Long count = productRepository.countProductsBySpecificCategory(category);
            categoryDistribution.put(category, count);
        }
        
        result.put("categoryDistribution", categoryDistribution);
        
        // Generate market insights
        List<String> insights = generateMarketInsights(markets, categories, averagePrices, productDistribution);
        result.put("insights", insights);
        
        return result;
    }
    
    /**
     * Generate insights about market data
     */
    private List<String> generateMarketInsights(
            List<String> markets, 
            List<String> categories, 
            Map<String, Map<String, Double>> averagePrices,
            Map<String, Long> productDistribution) {
        
        List<String> insights = new ArrayList<>();
        
        // Skip insights if no data
        if (markets.isEmpty()) {
            insights.add("No market data available for analysis.");
            return insights;
        }
        
        // Find market with lowest overall prices
        String cheapestMarket = null;
        double lowestAvgPrice = Double.MAX_VALUE;
        
        for (String market : markets) {
            Map<String, Double> marketPrices = averagePrices.get(market);
            if (marketPrices != null && marketPrices.containsKey("overall")) {
                double avg = marketPrices.get("overall");
                if (avg < lowestAvgPrice) {
                    lowestAvgPrice = avg;
                    cheapestMarket = market;
                }
            }
        }
        
        if (cheapestMarket != null) {
            insights.add(cheapestMarket + " offers the lowest average prices overall.");
        }
        
        // Find best market for each category
        for (String category : categories) {
            String bestMarket = null;
            double bestPrice = Double.MAX_VALUE;
            
            for (String market : markets) {
                Map<String, Double> marketPrices = averagePrices.get(market);
                if (marketPrices != null && marketPrices.containsKey(category)) {
                    double price = marketPrices.get(category);
                    if (price < bestPrice) {
                        bestPrice = price;
                        bestMarket = market;
                    }
                }
            }
            
            if (bestMarket != null) {
                insights.add(bestMarket + " has the best prices for " + category + " products.");
            }
        }
        
        // Find market with most products
        String marketWithMostProducts = null;
        long maxProducts = 0;
        
        for (Map.Entry<String, Long> entry : productDistribution.entrySet()) {
            if (entry.getValue() > maxProducts) {
                maxProducts = entry.getValue();
                marketWithMostProducts = entry.getKey();
            }
        }
        
        if (marketWithMostProducts != null) {
            insights.add(marketWithMostProducts + " has the largest product selection with " + maxProducts + " products.");
        }
        
        // Price difference insights
        if (markets.size() > 1) {
            // Find categories with biggest price variations
            Map<String, Double> priceVariationByCategory = new HashMap<>();
            
            for (String category : categories) {
                List<Double> prices = new ArrayList<>();
                
                for (String market : markets) {
                    Map<String, Double> marketPrices = averagePrices.get(market);
                    if (marketPrices != null && marketPrices.containsKey(category)) {
                        prices.add(marketPrices.get(category));
                    }
                }
                
                if (prices.size() > 1) {
                    double max = Collections.max(prices);
                    double min = Collections.min(prices);
                    double variation = (max - min) / min * 100.0; // Percentage variation
                    priceVariationByCategory.put(category, variation);
                }
            }
            
            // Get top 3 categories with highest price variation
            List<Map.Entry<String, Double>> sortedVariations = priceVariationByCategory.entrySet()
                    .stream()
                    .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
                    .limit(3)
                    .collect(Collectors.toList());
            
            for (Map.Entry<String, Double> entry : sortedVariations) {
                insights.add(String.format("%s products show significant price variation (%.1f%%) across markets.", 
                    entry.getKey(), entry.getValue()));
            }
        }
        
        return insights;
    }
}