import requests
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import quote


class AmazonProductScraper:
    """Scrape Amazon search results and extract product information."""
    
    def __init__(self):
        """Initialize the scraper with custom headers."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.base_url = 'https://www.amazon.com/s'
        self.timeout = 10
    
    def fetch_search_results(self, query: str) -> Optional[str]:
        """
        Fetch Amazon search results page HTML.
        
        Args:
            query (str): Search query string
            
        Returns:
            Optional[str]: HTML content of the search results page, or None if request fails
        """
        try:
            params = {'k': query}
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Amazon search results: {e}")
            return None
    
    def parse_products(self, html: str) -> List[Dict[str, str]]:
        """
        Parse HTML to extract product information.
        
        Args:
            html (str): HTML content from Amazon search page
            
        Returns:
            List[Dict[str, str]]: List of products with title, price, and image URL
        """
        products = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all product containers
            product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            if not product_containers:
                # Fallback to alternative selector
                product_containers = soup.find_all('div', {'class': 's-result-item'})
            
            for container in product_containers[:20]:  # Limit to 20 products
                try:
                    # Extract title
                    title_element = container.find('span', {'class': 'a-size-medium'})
                    if not title_element:
                        title_element = container.find('h2', {'class': 's-size-mini'})
                    
                    title = title_element.get_text(strip=True) if title_element else 'N/A'
                    
                    # Extract price
                    price_element = container.find('span', {'class': 'a-price-whole'})
                    if not price_element:
                        price_element = container.find('span', {'class': 'a-price'})
                    
                    price = price_element.get_text(strip=True) if price_element else 'N/A'
                    
                    # Extract image URL
                    img_element = container.find('img', {'class': 's-image'})
                    image_url = img_element.get('src', 'N/A') if img_element else 'N/A'
                    
                    # Skip products with missing critical information
                    if title == 'N/A':
                        continue
                    
                    product = {
                        'title': title,
                        'price': price,
                        'image_url': image_url
                    }
                    
                    products.append(product)
                
                except Exception as e:
                    print(f"Error parsing individual product: {e}")
                    continue
        
        except Exception as e:
            print(f"Error parsing HTML: {e}")
        
        return products
    
    def search_products(self, query: str) -> List[Dict[str, str]]:
        """
        Complete search workflow: fetch and parse Amazon results.
        
        Args:
            query (str): Search query string
            
        Returns:
            List[Dict[str, str]]: List of products with title, price, and image URL
        """
        if not query or not query.strip():
            print("Error: Search query cannot be empty")
            return []
        
        print(f"Searching Amazon for: {query}")
        
        # Fetch the page
        html = self.fetch_search_results(query)
        if not html:
            return []
        
        # Parse and return products
        products = self.parse_products(html)
        print(f"Found {len(products)} products")
        
        return products
    
    def search_products_json(self, query: str) -> str:
        """
        Search products and return as JSON string.
        
        Args:
            query (str): Search query string
            
        Returns:
            str: JSON formatted list of products
        """
        products = self.search_products(query)
        return json.dumps(products, indent=2)


# Standalone function for easy integration
def search_amazon(query: str) -> List[Dict[str, str]]:
    """
    Search Amazon and return product results.
    
    Args:
        query (str): Search query string
        
    Returns:
        List[Dict[str, str]]: List of products with title, price, and image URL
        
    Example:
        >>> results = search_amazon("wireless headphones")
        >>> print(results[0])
        {'title': '...', 'price': '...', 'image_url': '...'}
    """
    scraper = AmazonProductScraper()
    return scraper.search_products(query)


def search_amazon_json(query: str) -> str:
    """
    Search Amazon and return product results as JSON.
    
    Args:
        query (str): Search query string
        
    Returns:
        str: JSON formatted list of products
        
    Example:
        >>> json_results = search_amazon_json("wireless headphones")
        >>> print(json_results)
    """
    scraper = AmazonProductScraper()
    return scraper.search_products_json(query)


if __name__ == '__main__':
    # Example usage
    query = "wireless headphones"
    
    # Method 1: Get list of dictionaries
    products = search_amazon(query)
    for product in products[:5]:
        print(f"Title: {product['title']}")
        print(f"Price: {product['price']}")
        print(f"Image: {product['image_url']}")
        print("-" * 50)
    
    # Method 2: Get JSON string
    json_results = search_amazon_json(query)
    print("\nJSON Results:")
    print(json_results)
