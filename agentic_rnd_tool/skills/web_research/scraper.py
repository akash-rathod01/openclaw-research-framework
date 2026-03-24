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
            'delay': 1.0,
            # Tier 1 enhancements (backwards compatible)
            'use_javascript': False,  # Enable Selenium for JS rendering
            'max_depth_limit': 5,     # Maximum crawl depth allowed
            'max_sources_limit': 1000,  # Maximum sources allowed
            'extract_structured': True,  # Extract JSON-LD, Schema.org, etc.
            'domain_filter': True,    # Stay within same domain
            'auto_detect_js': True    # Auto-detect JS-heavy sites
        }
    
    def research(self, topic: str, max_sources: Optional[int] = None, 
                 depth: Optional[int] = None, use_javascript: Optional[bool] = None,
                 extract_structured: Optional[bool] = None, **kwargs) -> Dict:
        """
        Conduct research on a topic
        
        Args:
            topic: Research topic or query (can be URL or search term)
            max_sources: Maximum number of sources to gather
            depth: Link following depth (1-5)
            use_javascript: Enable JavaScript rendering (Selenium)
            extract_structured: Extract structured data (JSON-LD, Schema.org)
            
        Returns:
            Dictionary with research results
        """
        max_sources = max_sources or self.config['max_sources']
        depth = min(depth or self.config['depth'], self.config['max_depth_limit'])
        max_sources = min(max_sources, self.config['max_sources_limit'])
        
        # Tier 1: JavaScript rendering flag
        use_js = use_javascript if use_javascript is not None else self.config.get('use_javascript', False)
        
        # Tier 1: Structured data extraction flag
        extract_struct = extract_structured if extract_structured is not None else self.config.get('extract_structured', True)
        
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
        
        # Tier 1: Auto-detect JavaScript requirement
        if self.config.get('auto_detect_js') and not use_js:
            # Check if URL might need JS rendering (heuristic)
            for check_url in urls_to_scrape[:1]:  # Check first URL
                if self._might_need_javascript(check_url):
                    console.print("[yellow]🔍 JavaScript-heavy site detected, using Selenium...[/yellow]")
                    use_js = True
                    break
        
        # Store flags in config for scraping methods
        self.config['_active_use_js'] = use_js
        self.config['_active_extract_struct'] = extract_struct
        
        # Scrape the initial URL
        scraped_content = self.scrape_urls(urls_to_scrape, extract_links=(depth > 1), use_javascript=use_js)
        results['content'] = scraped_content['content']
        results['sources_scraped'] = len(scraped_content['content'])
        results['failed_urls'] = scraped_content.get('failed_urls', [])
        
        # Tier 1: Deep recursive crawling with domain filtering
        if depth > 1 and results['content']:
            base_domain = urlparse(urls_to_scrape[0]).netloc if self.config.get('domain_filter') else None
            
            for current_depth in range(2, depth + 1):
                if results['sources_scraped'] >= max_sources:
                    console.print(f"[yellow]⚠️  Reached max sources limit ({max_sources})[/yellow]")
                    break
                    
                all_links = []
                for item in results['content']:
                    if 'links' in item:
                        all_links.extend(item['links'])
                
                # Tier 1: Domain filtering
                if base_domain:
                    all_links = [link for link in all_links if urlparse(link).netloc == base_domain]
                
                # Remove already visited
                all_links = [link for link in all_links if link not in self.visited_urls]
                
                # Limit links to scrape
                remaining_quota = max_sources - results['sources_scraped']
                links_to_follow = list(set(all_links))[:remaining_quota]
                
                if not links_to_follow:
                    console.print(f"[cyan]ℹ️  No more links to follow at depth {current_depth}[/cyan]")
                    break
                
                console.print(f"[cyan]🔗 Following {len(links_to_follow)} links (depth {current_depth}/{depth})...[/cyan]")
                additional = self.scrape_urls(links_to_follow, extract_links=(current_depth < depth), use_javascript=use_js)
                results['content'].extend(additional['content'])
                results['sources_scraped'] += len(additional['content'])
                results['failed_urls'].extend(additional.get('failed_urls', []))
        
        # Generate summary
        total_text = ' '.join([item.get('content', '')[:500] for item in results['content']])
        results['summary'] = f"Scraped {results['sources_scraped']} pages. Total content: {len(total_text)} chars"
        
        print(f"✅ Research complete: {results['sources_scraped']} sources scraped")
        return results
    
    def scrape_urls(self, urls: List[str], extract_links: bool = False, use_javascript: bool = False) -> Dict:
        """
        Scrape multiple URLs in parallel
        
        Args:
            urls: List of URLs to scrape
            extract_links: Whether to extract links from pages
            use_javascript: Use Selenium for JavaScript rendering
            
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
                # Choose scraping method based on JavaScript flag
                scrape_method = self._scrape_with_js if use_javascript else self._scrape_single
                
                future_to_url = {
                    executor.submit(scrape_method, url, extract_links): url 
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
                result['links'] = links[:100]  # Increased for deep crawling
            
            # Tier 1: Extract structured data
            if self.config.get('_active_extract_struct', True):
                structured = self._extract_structured_data(soup, url)
                if structured:
                    result['structured_data'] = structured
            
            return result
            
        except Exception as e:
            print(f"⚠️  Error scraping {url}: {e}")
            return None
    
    def _scrape_with_js(self, url: str, extract_links: bool = False) -> Optional[Dict]:
        """
        Wrapper for JavaScript rendering using Selenium
        Tier 1: JavaScript rendering integration
        
        Args:
            url: URL to scrape
            extract_links: Whether to extract links
            
        Returns:
            Dictionary with page content
        """
        if url in self.visited_urls:
            return None
            
        self.visited_urls.add(url)
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'user-agent={self.config["user_agent"]}')
        
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(self.config['timeout'])
            driver.get(url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Scroll to trigger lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Get rendered HTML
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract title
            title = driver.title or 'No title'
            
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
                'title': title,
                'content': text[:5000],
                'timestamp': datetime.now().isoformat(),
                'status_code': 200,  # Assumed success
                'rendered_with': 'selenium'
            }
            
            # Extract links if requested
            if extract_links:
                links = []
                for link in soup.find_all('a', href=True):
                    absolute_url = urljoin(url, link['href'])
                    if self._is_valid_url(absolute_url):
                        links.append(absolute_url)
                result['links'] = links[:100]
            
            # Extract structured data
            if self.config.get('_active_extract_struct', True):
                structured = self._extract_structured_data(soup, url)
                if structured:
                    result['structured_data'] = structured
            
            driver.quit()
            return result
            
        except Exception as e:
            if driver:
                driver.quit()
            console.print(f"[red]❌ JS scraping error for {url}: {e}[/red]")
            return None
    
    def scrape_dynamic(self, url: str, wait_for_element: Optional[str] = None,
                      scroll: bool = False) -> Optional[Dict]:
        """
        Scrape JavaScript-heavy sites using Selenium (legacy method)
        Use _scrape_with_js() instead for new code
        
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
    
    def _might_need_javascript(self, url: str) -> bool:
        """
        Tier 1: Heuristic to detect if URL might need JavaScript rendering
        
        Args:
            url: URL to check
            
        Returns:
            True if site likely needs JS rendering
        """
        # Quick check of URL patterns that commonly use heavy JS
        js_indicators = [
            'app', 'dashboard', 'portal', 'platform',
            'react', 'angular', 'vue', 'next', 'nuxt'
        ]
        
        url_lower = url.lower()
        for indicator in js_indicators:
            if indicator in url_lower:
                return True
        
        # Quick HEAD request to check for SPA indicators
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            content_type = response.headers.get('content-type', '')
            
            # Some SPAs serve as application/json or have minimal HTML
            if 'application/json' in content_type:
                return True
                
        except Exception:
            pass  # If HEAD fails, fallback to static scraping
        
        return False
    
    def _extract_structured_data(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Tier 1: Extract structured data from HTML
        Extracts JSON-LD, Schema.org microdata, OpenGraph, and tables
        
        Args:
            soup: BeautifulSoup object
            url: Source URL
            
        Returns:
            Dictionary with structured data
        """
        structured = {}
        
        # 1. Extract JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            json_ld_data = []
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    json_ld_data.append(data)
                except (json.JSONDecodeError, AttributeError):
                    pass
            if json_ld_data:
                structured['json_ld'] = json_ld_data
        
        # 2. Extract OpenGraph tags
        og_data = {}
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            prop = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if prop and content:
                og_data[prop] = content
        if og_data:
            structured['opengraph'] = og_data
        
        # 3. Extract Schema.org microdata (simplified)
        schema_items = soup.find_all(attrs={'itemtype': True})
        if schema_items:
            schema_data = []
            for item in schema_items[:5]:  # Limit to first 5
                item_type = item.get('itemtype', '')
                item_data = {'type': item_type, 'properties': {}}
                
                # Extract itemprops
                props = item.find_all(attrs={'itemprop': True})
                for prop in props:
                    prop_name = prop.get('itemprop')
                    prop_value = prop.get('content') or prop.get_text(strip=True)
                    if prop_name:
                        item_data['properties'][prop_name] = prop_value[:200]  # Limit length
                
                schema_data.append(item_data)
            
            if schema_data:
                structured['schema_org'] = schema_data
        
        # 4. Extract meta tags
        meta_data = {}
        meta_tags = soup.find_all('meta', attrs={'name': True, 'content': True})
        for tag in meta_tags:
            name = tag.get('name', '')
            content = tag.get('content', '')
            if name and content:
                meta_data[name] = content
        if meta_data:
            structured['meta_tags'] = meta_data
        
        # 5. Extract tables (simplified)
        tables = soup.find_all('table')
        if tables:
            table_data = []
            for table in tables[:3]:  # Limit to first 3 tables
                headers = []
                rows = []
                
                # Extract headers
                thead = table.find('thead')
                if thead:
                    ths = thead.find_all('th')
                    headers = [th.get_text(strip=True) for th in ths]
                
                # Extract rows
                tbody = table.find('tbody') or table
                trs = tbody.find_all('tr')[:10]  # Max 10 rows
                for tr in trs:
                    cells = tr.find_all(['td', 'th'])
                    row = [cell.get_text(strip=True) for cell in cells]
                    if row:
                        rows.append(row)
                
                if headers or rows:
                    table_data.append({
                        'headers': headers,
                        'rows': rows[:10],
                        'total_rows': len(rows)
                    })
            
            if table_data:
                structured['tables'] = table_data
        
        return structured if structured else None
    
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