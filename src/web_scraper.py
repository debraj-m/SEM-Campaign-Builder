import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import logging
import time
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """Web scraper for extracting content from brand and competitor websites"""
    
    def __init__(self, user_agent: str = None):
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        
    def get_chrome_driver(self, headless: bool = True) -> webdriver.Chrome:
        """Initialize Chrome driver with optimal settings"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"--user-agent={self.user_agent}")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return driver
    
    def extract_basic_content(self, url: str) -> Dict[str, any]:
        """Extract basic content from a website using requests"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic elements
            title = soup.find('title').get_text().strip() if soup.find('title') else ""
            
            # Extract meta description
            meta_desc = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_desc = meta_tag.get('content', '').strip()
            
            # Extract headings
            headings = {
                'h1': [h.get_text().strip() for h in soup.find_all('h1')],
                'h2': [h.get_text().strip() for h in soup.find_all('h2')],
                'h3': [h.get_text().strip() for h in soup.find_all('h3')]
            }
            
            # Extract main text content
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text_content = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)
            
            return {
                'url': url,
                'title': title,
                'meta_description': meta_desc,
                'headings': headings,
                'content': text_content,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'status': 'error'
            }
    
    def extract_product_info(self, url: str) -> Dict[str, any]:
        """Extract product/service information with enhanced scraping"""
        driver = None
        try:
            driver = self.get_chrome_driver()
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract enhanced content
            result = {
                'url': url,
                'title': driver.title,
                'products': [],
                'services': [],
                'categories': [],
                'pricing_indicators': [],
                'navigation_items': [],
                'status': 'success'
            }
            
            # Extract navigation menu items
            nav_selectors = ['nav a', '.nav a', '.menu a', '.navigation a', 'header a']
            for selector in nav_selectors:
                try:
                    nav_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in nav_elements:
                        text = element.text.strip()
                        if text and len(text) > 1:
                            result['navigation_items'].append(text)
                except:
                    continue
            
            # Look for product/service indicators
            product_selectors = [
                '.product', '.service', '.category',
                '[class*="product"]', '[class*="service"]',
                'h1, h2, h3', '.title', '.heading'
            ]
            
            for selector in product_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) > 2:
                            # Categorize based on keywords
                            text_lower = text.lower()
                            if any(word in text_lower for word in ['product', 'item', 'buy', 'shop']):
                                result['products'].append(text)
                            elif any(word in text_lower for word in ['service', 'consulting', 'solution']):
                                result['services'].append(text)
                            elif any(word in text_lower for word in ['category', 'department', 'section']):
                                result['categories'].append(text)
                except:
                    continue
            
            # Look for pricing indicators
            price_patterns = [r'\$\d+', r'€\d+', r'£\d+', r'price', r'cost', r'pricing']
            page_source = driver.page_source.lower()
            
            for pattern in price_patterns:
                matches = re.findall(pattern, page_source)
                result['pricing_indicators'].extend(matches)
            
            # Remove duplicates and clean up
            for key in ['products', 'services', 'categories', 'navigation_items']:
                result[key] = list(set(result[key]))
                result[key] = [item for item in result[key] if len(item.strip()) > 2]
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting product info from {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'status': 'error'
            }
        finally:
            if driver:
                driver.quit()
    
    def generate_seed_keywords(self, brand_url: str, competitor_url: str = None) -> List[str]:
        """Generate seed keywords from website analysis"""
        keywords = set()
        
        # Analyze brand website
        brand_content = self.extract_product_info(brand_url)
        if brand_content['status'] == 'success':
            keywords.update(brand_content.get('products', []))
            keywords.update(brand_content.get('services', []))
            keywords.update(brand_content.get('categories', []))
            keywords.update(brand_content.get('navigation_items', []))
        
        # Analyze competitor website if provided
        if competitor_url:
            competitor_content = self.extract_product_info(competitor_url)
            if competitor_content['status'] == 'success':
                keywords.update(competitor_content.get('products', []))
                keywords.update(competitor_content.get('services', []))
                keywords.update(competitor_content.get('categories', []))
        
        # Clean and filter keywords
        cleaned_keywords = []
        for keyword in keywords:
            # Remove special characters and normalize
            cleaned = re.sub(r'[^\w\s]', '', keyword).strip()
            if len(cleaned) > 2 and len(cleaned.split()) <= 4:  # Keep reasonable length
                cleaned_keywords.append(cleaned.lower())
        
        return list(set(cleaned_keywords))[:20]  # Return top 20 unique keywords
    
    def analyze_competitor_content(self, competitor_url: str) -> Dict[str, any]:
        """Comprehensive competitor analysis"""
        basic_content = self.extract_basic_content(competitor_url)
        product_info = self.extract_product_info(competitor_url)
        
        return {
            'basic_content': basic_content,
            'product_info': product_info,
            'analysis_summary': {
                'total_products': len(product_info.get('products', [])),
                'total_services': len(product_info.get('services', [])),
                'content_length': len(basic_content.get('content', '')),
                'has_pricing': len(product_info.get('pricing_indicators', [])) > 0
            }
        }
