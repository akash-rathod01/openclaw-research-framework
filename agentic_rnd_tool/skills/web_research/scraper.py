"""
Web Research Agent - Autonomous web scraping and research capabilities
Part of the Agentic RnD Tool multi-agent framework
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Rich console output
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()


class WebResearcher:
    """
    Autonomous web research agent with scraping capabilities
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the web researcher
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or self._default_config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.get('user_agent', 'ResearchBot/1.0')
        })
        self.visited_urls = set()
        self.failed_urls = []
        
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'max_sources': 50,
            'depth': 2,
            'timeout': 30,
            'max_concurrent': 10,
            'respect_robots': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'max_retries': 3,
            'delay': 1.0
        }
    
    def research(self, topic: str, max_sources: Optional[int] = None, 
                 depth: Optional[int] = None, **kwargs) -> Dict:
        """
        Conduct research on a topic
        
        Args:
            topic: Research topic or query (can be URL or search term)
            max_sources: Maximum number of sources to gather
            depth: Link following depth (1-5)
            
        Returns:
            Dictionary with research results
        """
        max_sources = max_sources or self.config['max_sources']
        depth = depth or self.config['depth']
        
        print(f"🔍 Starting research on: {topic}")
        print(f"📊 Max sources: {max_sources}, Depth: {depth}")
        
        # Check if topic is a URL or search term
        if topic.startswith('http://') or topic.startswith('https://'):
            # Direct URL scraping
            print(f"📄 Detected URL - scraping directly")
            urls_to_scrape = [topic]
        else:
            # For search terms, we'd normally use a search API
            # For now, return informative message
            print(f"💡 Search term detected: '{topic}'")
            print(f"   To scrape a specific site, provide full URL")
            urls_to_scrape = []
        
        results = {
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'sources_found': len(urls_to_scrape),
            'sources_scraped': 0,
            'content': [],
            'summary': '',
            'failed_urls': []
        }
        
        if not urls_to_scrape:
            results['summary'] = f"No URLs to scrape for: {topic}. Provide a direct URL."
            print(f"⚠️  No URLs to scrape. Provide direct URLs.")
            return results
        
        # Scrape the initial URL
        scraped_content = self.scrape_urls(urls_to_scrape, extract_links=(depth > 1))
        results['content'] = scraped_content['content']
        results['sources_scraped'] = len(scraped_content['content'])
        results['failed_urls'] = scraped_content.get('failed_urls', [])
        
        # Follow links if depth > 1
        if depth > 1 and results['content']:
            all_links = []
            for item in results['content']:
                if 'links' in item:
                    all_links.extend(item['links'])
            
            # Limit links to scrape
            links_to_follow = list(set(all_links))[:max_sources - results['sources_scraped']]
            
            if links_to_follow:
                print(f"🔗 Following {len(links_to_follow)} links (depth {depth})...")
                additional = self.scrape_urls(links_to_follow, extract_links=False)
                results['content'].extend(additional['content'])
                results['sources_scraped'] += len(additional['content'])
                results['failed_urls'].extend(additional.get('failed_urls', []))
        
        # Generate summary
        total_text = ' '.join([item.get('content', '')[:500] for item in results['content']])
        results['summary'] = f"Scraped {results['sources_scraped']} pages. Total content: {len(total_text)} chars"
        
        print(f"✅ Research complete: {results['sources_scraped']} sources scraped")
        return results
    
    def scrape_urls(self, urls: List[str], extract_links: bool = False) -> Dict:
        """
        Scrape multiple URLs in parallel
        
        Args:
            urls: List of URLs to scrape
            extract_links: Whether to extract links from pages
            
        Returns:
            Dictionary with scraped content
        """
        console.print(f"[cyan]🕷️  Scraping {len(urls)} URLs...[/cyan]")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'urls_requested': len(urls),
            'content': [],
            'failed_urls': []
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Scraping pages...", total=len(urls))
            
            with ThreadPoolExecutor(max_workers=self.config['max_concurrent']) as executor:
                future_to_url = {
                    executor.submit(self._scrape_single, url, extract_links): url 
                    for url in urls
                }
                
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        result = future.result()
                        if result:
                            results['content'].append(result)
                        time.sleep(self.config['delay'])  # Polite crawling
                    except Exception as e:
                        console.print(f"[red]❌ Failed: {url[:50]}...[/red]")
                        results['failed_urls'].append({'url': url, 'error': str(e)})
                    
                    progress.update(task, advance=1)
        
        console.print(f"[green]✅ Scraped {len(results['content'])} URLs successfully[/green]")
        if results['failed_urls']:
            console.print(f"[yellow]⚠️  Failed: {len(results['failed_urls'])} URLs[/yellow]")
        
        return results
    
    def _scrape_single(self, url: str, extract_links: bool = False) -> Optional[Dict]:
        """
        Scrape a single URL
        
        Args:
            url: URL to scrape
            extract_links: Extract links from page
            
        Returns:
            Dictionary with page content or None
        """
        if url in self.visited_urls:
            return None
            
        self.visited_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=self.config['timeout'])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            title = soup.find('title')
            title_text = title.get_text().strip() if title else 'No title'
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            result = {
                'url': url,
                'title': title_text,
                'content': text[:5000],  # Limit content size
                'timestamp': datetime.now().isoformat(),
                'status_code': response.status_code
            }
            
            # Extract links if requested
            if extract_links:
                links = []
                for link in soup.find_all('a', href=True):
                    absolute_url = urljoin(url, link['href'])
                    if self._is_valid_url(absolute_url):
                        links.append(absolute_url)
                result['links'] = links[:50]  # Limit links
            
            return result
            
        except Exception as e:
            print(f"⚠️  Error scraping {url}: {e}")
            return None
    
    def scrape_dynamic(self, url: str, wait_for_element: Optional[str] = None,
                      scroll: bool = False) -> Optional[Dict]:
        """
        Scrape JavaScript-heavy sites using Selenium
        
        Args:
            url: URL to scrape
            wait_for_element: CSS selector to wait for
            scroll: Whether to scroll page to load content
            
        Returns:
            Dictionary with page content
        """
        print(f"🌐 Scraping dynamic site: {url}")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # Wait for element if specified
            if wait_for_element:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element))
                )
            
            # Scroll to load content
            if scroll:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Get page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            result = {
                'url': url,
                'title': driver.title,
                'content': soup.get_text()[:5000],
                'timestamp': datetime.now().isoformat()
            }
            
            driver.quit()
            return result
            
        except Exception as e:
            print(f"❌ Error with dynamic scraping: {e}")
            return None
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and should be followed"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def save_results(self, results: Dict, filename: str = None) -> str:
        """
        Save research results to file
        
        Args:
            results: Results dictionary
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filename}")
        return filename


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    researcher = WebResearcher()
    
    if len(sys.argv) > 1:
        topic = ' '.join(sys.argv[1:])
        results = researcher.research(topic)
        researcher.save_results(results)
    else:
        print("Usage: python scraper.py <research topic>")
        print("Example: python scraper.py AI frameworks 2026")