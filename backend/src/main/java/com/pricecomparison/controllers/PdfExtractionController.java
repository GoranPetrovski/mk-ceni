package com.pricecomparison.controllers;

import com.pricecomparison.services.PdfExtractionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@Slf4j
public class PdfExtractionController {

    private final PdfExtractionService pdfExtractionService;
    
    @PostMapping("/extract-prices")
    public ResponseEntity<Map<String, Object>> extractPricesFromPdf(
            @RequestParam("files") List<MultipartFile> files) {
        
        if (files == null || files.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of(
                "message", "No files were uploaded",
                "success", false
            ));
        }
        
        try {
            int extractedProducts = pdfExtractionService.extractPricesFromPdfs(files);
            
            return ResponseEntity.ok(Map.of(
                "message", String.format("Successfully extracted data from %d files", files.size()),
                "products", extractedProducts,
                "success", true
            ));
        } catch (Exception e) {
            log.error("Error extracting prices from PDFs", e);
            return ResponseEntity.badRequest().body(Map.of(
                "message", "Error extracting data: " + e.getMessage(),
                "success", false
            ));
        }
    }
}