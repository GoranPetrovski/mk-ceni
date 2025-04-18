package com.pricecomparison.services;

import com.pricecomparison.models.Product;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
@RequiredArgsConstructor
@Slf4j
public class PdfExtractionService {

    private final ProductService productService;

    /**
     * Extract product prices from PDF files
     * @param files PDF files containing product prices
     * @return Number of products extracted
     */
    public int extractPricesFromPdfs(List<MultipartFile> files) {
        int totalProducts = 0;
        
        for (MultipartFile file : files) {
            try {
                List<Product> extractedProducts = extractProductsFromPdf(file);
                productService.saveAll(extractedProducts);
                totalProducts += extractedProducts.size();
                log.info("Extracted {} products from file: {}", extractedProducts.size(), file.getOriginalFilename());
            } catch (IOException e) {
                log.error("Error extracting data from PDF: {}", file.getOriginalFilename(), e);
            }
        }
        
        return totalProducts;
    }
    
    /**
     * Extract products from a single PDF file
     * @param file PDF file
     * @return List of extracted products
     */
    private List<Product> extractProductsFromPdf(MultipartFile file) throws IOException {
        List<Product> products = new ArrayList<>();
        String marketName = extractMarketFromFilename(file.getOriginalFilename());
        
        try (PDDocument document = PDDocument.load(file.getInputStream())) {
            PDFTextStripper stripper = new PDFTextStripper();
            String text = stripper.getText(document);
            
            // If market name couldn't be extracted from filename, try from content
            if (marketName == null || marketName.isEmpty()) {
                marketName = extractMarketFromContent(text);
            }
            
            // Fall back to filename without extension if market still not identified
            if (marketName == null || marketName.isEmpty()) {
                marketName = file.getOriginalFilename().replaceFirst("[.][^.]+$", "");
            }
            
            // Extract product information using various patterns
            products.addAll(extractProductsFromText(text, marketName));
        }
        
        return products;
    }
    
    /**
     * Extract market name from the PDF filename
     */
    private String extractMarketFromFilename(String filename) {
        if (filename == null) return "";
        
        // Remove file extension
        String nameWithoutExt = filename.replaceFirst("[.][^.]+$", "");
        
        // Look for common market name patterns
        Pattern pattern = Pattern.compile("(\\w+)[-_]prices|prices[-_](\\w+)|catalog[-_](\\w+)|(\\w+)[-_]catalog", 
                                        Pattern.CASE_INSENSITIVE);
        Matcher matcher = pattern.matcher(nameWithoutExt);
        
        if (matcher.find()) {
            for (int i = 1; i <= matcher.groupCount(); i++) {
                if (matcher.group(i) != null) {
                    return matcher.group(i);
                }
            }
        }
        
        return nameWithoutExt; // Return filename if no pattern matches
    }
    
    /**
     * Extract market name from the PDF content
     */
    private String extractMarketFromContent(String text) {
        // Look for common headers or footers with market names
        Pattern pattern = Pattern.compile("(^|\\n)\\s*(.*?market|.*?store|.*?supermarket|.*?shop)\\s*($|\\n)", 
                                        Pattern.CASE_INSENSITIVE);
        Matcher matcher = pattern.matcher(text);
        
        if (matcher.find() && matcher.group(2) != null) {
            return matcher.group(2).trim();
        }
        
        // Try looking for a header that might be the store name
        pattern = Pattern.compile("(^|\\n)\\s*([A-Z][A-Za-z ]{2,30})\\s*($|\\n)");
        matcher = pattern.matcher(text);
        
        if (matcher.find() && matcher.group(2) != null) {
            return matcher.group(2).trim();
        }
        
        return "Unknown Market";
    }
    
    /**
     * Extract product information from text
     */
    private List<Product> extractProductsFromText(String text, String marketName) {
        List<Product> products = new ArrayList<>();
        
        // Multiple pattern matching for different price formats
        List<Pattern> patterns = new ArrayList<>();
        
        // Pattern 1: Product name followed by price
        patterns.add(Pattern.compile("([A-Za-z0-9 \\-&'.]+)\\s*[$€£]\\s*(\\d+\\.\\d{2})", Pattern.MULTILINE));
        
        // Pattern 2: Product name with price at the end of line
        patterns.add(Pattern.compile("([A-Za-z0-9 \\-&'.]+?)\\s+[$€£]?\\s*(\\d+\\.\\d{2})\\s*$", Pattern.MULTILINE));
        
        // Pattern 3: Price followed by product name
        patterns.add(Pattern.compile("[$€£]\\s*(\\d+\\.\\d{2})\\s+([A-Za-z0-9 \\-&'.]+)", Pattern.MULTILINE));
        
        for (Pattern pattern : patterns) {
            Matcher matcher = pattern.matcher(text);
            
            while (matcher.find()) {
                try {
                    String productName;
                    double price;
                    
                    if (pattern.pattern().startsWith("[$€£]")) {
                        // Handle Pattern 3 (price first)
                        productName = matcher.group(2).trim();
                        price = Double.parseDouble(matcher.group(1));
                    } else {
                        // Handle Pattern 1 and 2 (product name first)
                        productName = matcher.group(1).trim();
                        price = Double.parseDouble(matcher.group(2));
                    }
                    
                    // Skip if product name too short or looks like a page number
                    if (productName.length() < 3 || productName.matches("\\d+")) {
                        continue;
                    }
                    
                    // Extract category if possible
                    String category = extractCategory(productName, text);
                    
                    Product product = Product.builder()
                            .name(productName)
                            .price(price)
                            .category(category)
                            .market(marketName)
                            .build();
                    
                    products.add(product);
                } catch (NumberFormatException e) {
                    log.warn("Failed to parse price for pattern match: {}", matcher.group(0));
                }
            }
        }
        
        return products;
    }
    
    /**
     * Extract category based on product name or surrounding text
     */
    private String extractCategory(String productName, String text) {
        // Common category keywords
        String[][] categoryKeywords = {
            {"fruit", "apple", "banana", "orange", "grape", "berry", "pear", "peach", "plum", "melon"},
            {"vegetable", "carrot", "potato", "tomato", "onion", "lettuce", "pepper", "cucumber", "broccoli"},
            {"dairy", "milk", "cheese", "yogurt", "butter", "cream", "egg"},
            {"meat", "beef", "pork", "chicken", "turkey", "lamb", "steak", "ham", "sausage"},
            {"bakery", "bread", "cake", "pastry", "muffin", "cookie", "roll", "bake"},
            {"beverage", "drink", "water", "juice", "soda", "coffee", "tea", "alcohol", "wine", "beer"},
            {"snack", "chip", "crisp", "pretzel", "popcorn", "nuts", "candy", "chocolate"},
            {"seafood", "fish", "shrimp", "prawn", "crab", "lobster", "oyster", "mussel", "tuna", "salmon"},
            {"household", "cleaning", "detergent", "soap", "paper", "towel", "tissue", "brush", "sponge"},
            {"personal care", "toothpaste", "shampoo", "soap", "lotion", "deodorant", "toilet"}
        };
        
        String productNameLower = productName.toLowerCase();
        
        // Check if product name contains category keywords
        for (String[] categoryGroup : categoryKeywords) {
            String category = categoryGroup[0];
            for (String keyword : categoryGroup) {
                if (productNameLower.contains(keyword)) {
                    return capitalize(category);
                }
            }
        }
        
        // Try to find category from context (lines above the product)
        String[] lines = text.split("\\n");
        for (int i = 0; i < lines.length; i++) {
            if (lines[i].contains(productName)) {
                // Look at up to 3 lines above for category headers
                for (int j = Math.max(0, i - 3); j < i; j++) {
                    String line = lines[j].trim();
                    // Category headers are often short, all caps or have specific formatting
                    if (line.length() > 0 && line.length() < 30 && 
                        (line.equals(line.toUpperCase()) || line.endsWith(":"))) {
                        for (String[] categoryGroup : categoryKeywords) {
                            String category = categoryGroup[0];
                            for (String keyword : categoryGroup) {
                                if (line.toLowerCase().contains(keyword)) {
                                    return capitalize(category);
                                }
                            }
                        }
                        // If line looks like a header and doesn't match keywords, use it as category
                        if (line.length() < 20 && !line.contains("$") && !line.matches(".*\\d.*")) {
                            return capitalize(line.replaceAll("[:;]$", ""));
                        }
                    }
                }
                break;
            }
        }
        
        return null;
    }
    
    private String capitalize(String str) {
        if (str == null || str.isEmpty()) {
            return str;
        }
        return str.substring(0, 1).toUpperCase() + str.substring(1);
    }
}