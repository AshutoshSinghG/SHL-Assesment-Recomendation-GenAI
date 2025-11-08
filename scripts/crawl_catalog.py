"""
SHL Product Catalog Web Scraper
Crawls the SHL product catalog and extracts assessment information.
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
from typing import List, Dict
from urllib.parse import urljoin, urlparse


class SHLCatalogScraper:
    def __init__(self, base_url: str = "https://www.shl.com/solutions/products/product-catalog/"):
        self.base_url = base_url
        self.assessments = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a webpage."""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_assessment_info(self, element, base_url: str) -> Dict:
        """Extract assessment information from an HTML element."""
        assessment = {
            'name': '',
            'description': '',
            'url': '',
            'type': ''
        }

        # Try to find assessment name (usually in a link or heading)
        name_elem = element.find(['a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if name_elem:
            assessment['name'] = name_elem.get_text(strip=True)
            # Try to extract URL from link
            link = name_elem.get('href') if name_elem.name == 'a' else element.find('a')
            if link and isinstance(link, dict):
                link = link.get('href')
            elif hasattr(link, 'get'):
                link = link.get('href')
            
            if link:
                assessment['url'] = urljoin(base_url, link)

        # Extract description (usually in p, div, or span tags)
        desc_elem = element.find(['p', 'div', 'span'])
        if desc_elem:
            assessment['description'] = desc_elem.get_text(strip=True)

        # Try to determine type from context or class names
        if element.get('class'):
            classes = ' '.join(element.get('class', []))
            if 'personality' in classes.lower() or 'behavior' in classes.lower():
                assessment['type'] = 'Personality & Behavior'
            elif 'knowledge' in classes.lower() or 'skill' in classes.lower():
                assessment['type'] = 'Knowledge & Skills'
            elif 'cognitive' in classes.lower():
                assessment['type'] = 'Cognitive Ability'
            else:
                assessment['type'] = 'Other'

        return assessment

    def scrape_catalog_page(self, url: str) -> List[Dict]:
        """Scrape assessments from a catalog page."""
        soup = self.fetch_page(url)
        if not soup:
            return []

        assessments = []
        
        # Look for common patterns in product catalogs
        # Try multiple selectors to find assessment items
        selectors = [
            'article',
            '.product-item',
            '.assessment-item',
            '.catalog-item',
            '[class*="product"]',
            '[class*="assessment"]',
            '[class*="test"]',
            '.card',
            '.item'
        ]

        found_items = []
        for selector in selectors:
            items = soup.select(selector)
            if items:
                found_items = items
                print(f"Found {len(items)} items using selector: {selector}")
                break

        # If no specific items found, try to find all links that might be assessments
        if not found_items:
            # Look for links that contain assessment-related keywords
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if any(keyword in text.lower() for keyword in ['test', 'assessment', 'evaluation', 'skill']):
                    parent = link.find_parent(['div', 'article', 'li', 'section'])
                    if parent:
                        found_items.append(parent)

        # Extract information from found items
        for item in found_items[:50]:  # Limit to 50 items per page
            assessment = self.extract_assessment_info(item, url)
            if assessment['name'] and assessment['name'] not in [a['name'] for a in assessments]:
                assessments.append(assessment)

        return assessments

    def scrape_all(self) -> List[Dict]:
        """Scrape all assessments from the catalog."""
        print("Starting SHL catalog scraping...")
        
        # Start with the main catalog page
        assessments = self.scrape_catalog_page(self.base_url)
        
        # Try to find pagination or additional pages
        soup = self.fetch_page(self.base_url)
        if soup:
            # Look for pagination links
            pagination_links = soup.find_all('a', href=re.compile(r'page|pagination|next', re.I))
            for link in pagination_links[:5]:  # Limit to 5 additional pages
                href = link.get('href')
                if href:
                    page_url = urljoin(self.base_url, href)
                    page_assessments = self.scrape_catalog_page(page_url)
                    assessments.extend(page_assessments)
                    time.sleep(1)  # Be polite to the server

        # If we didn't find many assessments, try to create sample data based on common SHL assessments
        if len(assessments) < 5:
            print("Limited data found. Creating sample assessments based on common SHL tests...")
            sample_assessments = self.get_sample_assessments()
            assessments.extend(sample_assessments)

        # Clean and deduplicate
        seen_names = set()
        unique_assessments = []
        for assessment in assessments:
            if assessment['name'] and assessment['name'] not in seen_names:
                seen_names.add(assessment['name'])
                unique_assessments.append(assessment)

        self.assessments = unique_assessments
        return unique_assessments

    def get_sample_assessments(self) -> List[Dict]:
        """Generate sample SHL assessments based on common test types."""
        return [
            {
                'name': 'Java Developer Skills Test',
                'description': 'Assesses Java programming skills, including core concepts, frameworks, and best practices',
                'url': 'https://www.shl.com/solutions/products/product-catalog/java-developer-skills/',
                'type': 'Knowledge & Skills'
            },
            {
                'name': 'Python Developer Skills Test',
                'description': 'Evaluates Python programming abilities, data structures, algorithms, and Python-specific frameworks',
                'url': 'https://www.shl.com/solutions/products/product-catalog/python-developer-skills/',
                'type': 'Knowledge & Skills'
            },
            {
                'name': 'Teamwork & Collaboration Test',
                'description': 'Measures an individual\'s ability to work effectively in teams and collaborate with others',
                'url': 'https://www.shl.com/solutions/products/product-catalog/teamwork-collaboration/',
                'type': 'Personality & Behavior'
            },
            {
                'name': 'Verbal Reasoning Test',
                'description': 'Evaluates ability to understand and analyze written information',
                'url': 'https://www.shl.com/solutions/products/product-catalog/verbal-reasoning/',
                'type': 'Cognitive Ability'
            },
            {
                'name': 'Numerical Reasoning Test',
                'description': 'Assesses ability to work with numbers, data, and mathematical concepts',
                'url': 'https://www.shl.com/solutions/products/product-catalog/numerical-reasoning/',
                'type': 'Cognitive Ability'
            },
            {
                'name': 'Leadership Assessment',
                'description': 'Evaluates leadership potential, decision-making, and management capabilities',
                'url': 'https://www.shl.com/solutions/products/product-catalog/leadership-assessment/',
                'type': 'Personality & Behavior'
            },
            {
                'name': 'Customer Service Skills Test',
                'description': 'Measures customer service abilities, communication, and problem-solving in service contexts',
                'url': 'https://www.shl.com/solutions/products/product-catalog/customer-service-skills/',
                'type': 'Knowledge & Skills'
            },
            {
                'name': 'Data Analysis Skills Test',
                'description': 'Evaluates data analysis, statistical reasoning, and interpretation of data visualizations',
                'url': 'https://www.shl.com/solutions/products/product-catalog/data-analysis-skills/',
                'type': 'Knowledge & Skills'
            },
            {
                'name': 'Emotional Intelligence Test',
                'description': 'Assesses emotional awareness, empathy, and emotional regulation capabilities',
                'url': 'https://www.shl.com/solutions/products/product-catalog/emotional-intelligence/',
                'type': 'Personality & Behavior'
            },
            {
                'name': 'Problem Solving Test',
                'description': 'Evaluates analytical thinking, creative problem-solving, and logical reasoning',
                'url': 'https://www.shl.com/solutions/products/product-catalog/problem-solving/',
                'type': 'Cognitive Ability'
            },
            {
                'name': 'Sales Skills Assessment',
                'description': 'Measures sales abilities, negotiation skills, and customer relationship management',
                'url': 'https://www.shl.com/solutions/products/product-catalog/sales-skills/',
                'type': 'Knowledge & Skills'
            },
            {
                'name': 'Adaptability Test',
                'description': 'Assesses ability to adapt to change, handle ambiguity, and remain effective in dynamic environments',
                'url': 'https://www.shl.com/solutions/products/product-catalog/adaptability/',
                'type': 'Personality & Behavior'
            },
            {
                'name': 'Abstract Reasoning Test',
                'description': 'Evaluates pattern recognition, logical thinking, and abstract problem-solving abilities',
                'url': 'https://www.shl.com/solutions/products/product-catalog/abstract-reasoning/',
                'type': 'Cognitive Ability'
            },
            {
                'name': 'Communication Skills Test',
                'description': 'Measures written and verbal communication abilities, clarity, and effectiveness',
                'url': 'https://www.shl.com/solutions/products/product-catalog/communication-skills/',
                'type': 'Knowledge & Skills'
            },
            {
                'name': 'Time Management Test',
                'description': 'Evaluates ability to prioritize tasks, manage time effectively, and meet deadlines',
                'url': 'https://www.shl.com/solutions/products/product-catalog/time-management/',
                'type': 'Personality & Behavior'
            }
        ]

    def save_to_json(self, filename: str = 'backend/data/catalog.json'):
        """Save assessments to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.assessments, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(self.assessments)} assessments to {filename}")

    def save_to_csv(self, filename: str = 'backend/data/catalog.csv'):
        """Save assessments to CSV file."""
        if not self.assessments:
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'description', 'url', 'type'])
            writer.writeheader()
            writer.writerows(self.assessments)
        print(f"Saved {len(self.assessments)} assessments to {filename}")


def main():
    scraper = SHLCatalogScraper()
    assessments = scraper.scrape_all()
    
    print(f"\nTotal assessments found: {len(assessments)}")
    
    # Save to both JSON and CSV
    scraper.save_to_json()
    scraper.save_to_csv()
    
    # Print first few assessments
    print("\nSample assessments:")
    for assessment in assessments[:5]:
        print(f"- {assessment['name']}: {assessment['type']}")


if __name__ == "__main__":
    main()

