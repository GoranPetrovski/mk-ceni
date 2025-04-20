
package com.pricecomparison.services;

import com.pricecomparison.models.Product;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class WebScraperService {

    public List<Product> scrapeVeroPrices() {
        List<Product> products = new ArrayList<>();
        try {
            Document doc = Jsoup.connect("https://pricelist.vero.com.mk/91_2.html").get();
            Elements rows = doc.select("tr");
            String currentCategory = "General";

            for (Element row : rows) {
                Element th = row.selectFirst("th");
                if (th != null && !th.text().trim().isEmpty()) {
                    currentCategory = th.text().trim();
                    continue;
                }

                Elements cells = row.select("td");
                if (cells.size() >= 2) {
                    String name = cells.get(0).text().trim();
                    String priceText = cells.get(cells.size() - 1).text().trim();
                    
                    try {
                        double price = Double.parseDouble(priceText.replaceAll("[^\\d.]", ""));
                        if (price > 0 && price < 1000000) {
                            Product product = new Product();
                            product.setName(name);
                            product.setPrice(price);
                            product.setCategory(currentCategory);
                            product.setMarket("Vero");
                            products.add(product);
                        }
                    } catch (NumberFormatException e) {
                        log.warn("Could not parse price for product: {}", name);
                    }
                }
            }
        } catch (IOException e) {
            log.error("Error scraping Vero prices", e);
        }
        return products;
    }

    public List<Product> scrapeStokokmakPrices() {
        List<Product> products = new ArrayList<>();
        try {
            Document doc = Jsoup.connect("https://stokomak.com.mk/proverka-na-ceni/").get();
            Elements tables = doc.select("table.table");
            
            for (Element table : tables) {
                String category = "General";
                Element prevHeading = table.previousElementSibling();
                if (prevHeading != null && (prevHeading.is("h2") || prevHeading.is("h3") || prevHeading.is("h4"))) {
                    category = prevHeading.text().trim();
                }

                Elements rows = table.select("tr");
                for (int i = 1; i < rows.size(); i++) {
                    Element row = rows.get(i);
                    Elements cells = row.select("td");
                    
                    if (cells.size() >= 2) {
                        String name = cells.get(0).text().trim();
                        String priceText = cells.get(1).text().trim();
                        
                        try {
                            double price = Double.parseDouble(priceText.replaceAll("[^\\d.]", ""));
                            Product product = new Product();
                            product.setName(name);
                            product.setPrice(price);
                            product.setCategory(category);
                            product.setMarket("Stokomak");
                            products.add(product);
                        } catch (NumberFormatException e) {
                            log.warn("Could not parse price for product: {}", name);
                        }
                    }
                }
            }
        } catch (IOException e) {
            log.error("Error scraping Stokomak prices", e);
        }
        return products;
    }
}
