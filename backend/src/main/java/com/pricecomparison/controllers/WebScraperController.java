
package com.pricecomparison.controllers;

import com.pricecomparison.models.Product;
import com.pricecomparison.services.WebScraperService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/scrape")
@RequiredArgsConstructor
@Slf4j
public class WebScraperController {

    private final WebScraperService webScraperService;

    @GetMapping("/vero")
    public ResponseEntity<Map<String, Object>> scrapeVero() {
        try {
            List<Product> products = webScraperService.scrapeVeroPrices();
            return ResponseEntity.ok(Map.of(
                "message", "Successfully scraped Vero prices",
                "products", products,
                "count", products.size(),
                "success", true
            ));
        } catch (Exception e) {
            log.error("Error scraping Vero prices", e);
            return ResponseEntity.badRequest().body(Map.of(
                "message", "Error scraping Vero prices: " + e.getMessage(),
                "success", false
            ));
        }
    }

    @GetMapping("/stokomak") 
    public ResponseEntity<Map<String, Object>> scrapeStokomak() {
        try {
            List<Product> products = webScraperService.scrapeStokokmakPrices();
            return ResponseEntity.ok(Map.of(
                "message", "Successfully scraped Stokomak prices",
                "products", products,
                "count", products.size(),
                "success", true
            ));
        } catch (Exception e) {
            log.error("Error scraping Stokomak prices", e);
            return ResponseEntity.badRequest().body(Map.of(
                "message", "Error scraping Stokomak prices: " + e.getMessage(),
                "success", false
            ));
        }
    }
}
