package com.pricecomparison.controllers;

import com.pricecomparison.services.MarketAnalysisService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/market-analysis")
@RequiredArgsConstructor
@Slf4j
public class MarketAnalysisController {

    private final MarketAnalysisService marketAnalysisService;
    
    @GetMapping
    public ResponseEntity<Map<String, Object>> getMarketAnalysis() {
        return ResponseEntity.ok(marketAnalysisService.getMarketAnalysis());
    }
}