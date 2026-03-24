"""
Security Scanner Agent - OWASP ZAP integration for vulnerability assessment
Part of the Agentic RnD Tool multi-agent framework

⚠️ WARNING: Only scan applications you own or have explicit permission to test.
Unauthorized security testing is illegal.
"""

from zapv2 import ZAPv2
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from pathlib import Path


class SecurityScanner:
    """
    Autonomous security scanning agent using OWASP ZAP
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the security scanner
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or self._default_config()
        
        # Initialize ZAP API client
        try:
            self.zap = ZAPv2(
                apikey=self.config['zap_api_key'],
                proxies={
                    'http': f"http://{self.config['zap_host']}:{self.config['zap_port']}",
                    'https': f"http://{self.config['zap_host']}:{self.config['zap_port']}"
                }
            )
            # Test connection
            self.zap.core.version
            print("✅ Connected to OWASP ZAP")
        except Exception as e:
            print(f"⚠️  Warning: Could not connect to ZAP: {e}")
            print("   Make sure ZAP is running in daemon mode")
            self.zap = None
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'zap_api_key': 'changeme',
            'zap_host': 'localhost',
            'zap_port': 8080,
            'timeout': 3600,
            'report_dir': './reports',
            'intensity': 'medium'
        }
    
    def scan(self, target: str, scan_type: str = 'passive',
             report_format: List[str] = None, **kwargs) -> Dict:
        """
        Perform security scan on target
        
        Args:
            target: Target URL to scan
            scan_type: Type of scan ('passive', 'active', 'full')
            report_format: List of report formats ['html', 'json', 'xml']
            
        Returns:
            Dictionary with scan results
        """
        if not self.zap:
            return self._mock_scan_result(target, "ZAP not connected")
        
        print(f"🔒 Starting {scan_type} security scan on: {target}")
        
        report_format = report_format or ['html', 'json']
        scan_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = {
            'target': target,
            'scan_type': scan_type,
            'scan_id': scan_id,
            'scan_start': datetime.now().isoformat(),
            'scan_end': None,
            'alerts': [],
            'summary': {},
            'report_paths': {}
        }
        
        try:
            # Access the target
            print(f"🌐 Accessing target: {target}")
            self.zap.urlopen(target)
            time.sleep(2)
            
            # Spider the target
            if scan_type in ['active', 'full']:
                print("🕷️  Spidering target...")
                spider_id = self.zap.spider.scan(target)
                self._wait_for_spider(spider_id)
                print("✅ Spider complete")
            
            # Passive scan (always runs)
            print("🔍 Running passive scan...")
            time.sleep(5)  # Let passive scanner run
            
            # Active scan (if requested)
            if scan_type in ['active', 'full']:
                print("⚡ Running active scan (this may take a while)...")
                confirmation = kwargs.get('confirmed', False)
                if not confirmation:
                    print("⚠️  Active scan requires confirmation (add confirmed=True)")
                    print("💡 Continuing with passive scan only...")
                else:
                    scan_id = self.zap.ascan.scan(target)
                    self._wait_for_active_scan(scan_id)
                    print("✅ Active scan complete")
            
            # Get alerts
            alerts = self.zap.core.alerts(baseurl=target)
            results['alerts'] = self._process_alerts(alerts)
            results['summary'] = self._generate_summary(alerts)
            results['scan_end'] = datetime.now().isoformat()
            
            # Generate reports
            report_dir = Path(self.config['report_dir'])
            report_dir.mkdir(exist_ok=True)
            
            for fmt in report_format:
                report_path = self._generate_report(
                    target, scan_id, fmt, report_dir
                )
                results['report_paths'][fmt] = str(report_path)
            
            print(f"✅ Scan complete: {len(alerts)} alerts found")
            print(f"📊 Summary: {results['summary']}")
            
            return results
            
        except Exception as e:
            print(f"❌ Scan error: {e}")
            results['error'] = str(e)
            results['scan_end'] = datetime.now().isoformat()
            return results
    
    def _wait_for_spider(self, spider_id: str, timeout: int = 300):
        """Wait for spider to complete"""
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                print("⚠️  Spider timeout")
                break
            
            progress = int(self.zap.spider.status(spider_id))
            print(f"   Spider progress: {progress}%", end='\r')
            
            if progress >= 100:
                break
            
            time.sleep(2)
        print()  # New line after progress
    
    def _wait_for_active_scan(self, scan_id: str, timeout: int = 3600):
        """Wait for active scan to complete"""
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                print("⚠️  Active scan timeout")
                break
            
            progress = int(self.zap.ascan.status(scan_id))
            print(f"   Active scan progress: {progress}%", end='\r')
            
            if progress >= 100:
                break
            
            time.sleep(5)
        print()  # New line after progress
    
    def _process_alerts(self, alerts: List[Dict]) -> List[Dict]:
        """Process and structure alerts"""
        processed = []
        for alert in alerts:
            processed.append({
                'alert_id': alert.get('pluginId', ''),
                'name': alert.get('alert', ''),
                'risk': alert.get('risk', ''),
                'confidence': alert.get('confidence', ''),
                'description': alert.get('description', ''),
                'solution': alert.get('solution', ''),
                'url': alert.get('url', ''),
                'cwe_id': alert.get('cweid', ''),
                'wasc_id': alert.get('wascid', ''),
                'reference': alert.get('reference', '')
            })
        return processed
    
    def _generate_summary(self, alerts: List[Dict]) -> Dict:
        """Generate summary statistics"""
        summary = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'informational': 0
        }
        
        for alert in alerts:
            risk = alert.get('risk', '').lower()
            if risk == 'high':
                summary['high'] += 1
            elif risk == 'medium':
                summary['medium'] += 1
            elif risk == 'low':
                summary['low'] += 1
            elif risk == 'informational':
                summary['informational'] += 1
        
        return summary
    
    def _generate_report(self, target: str, scan_id: str, 
                        format: str, output_dir: Path) -> Path:
        """Generate scan report in specified format"""
        filename = f"scan_{scan_id}.{format}"
        filepath = output_dir / filename
        
        try:
            if format == 'html':
                report = self.zap.core.htmlreport()
            elif format == 'json':
                report = self.zap.core.jsonreport()
            elif format == 'xml':
                report = self.zap.core.xmlreport()
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"📄 Report saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"⚠️  Could not generate {format} report: {e}")
            return None
    
    def scan_api(self, openapi_spec: str, base_url: Optional[str] = None,
                 **kwargs) -> Dict:
        """
        Scan API using OpenAPI/Swagger specification
        
        Args:
            openapi_spec: Path or URL to OpenAPI spec
            base_url: Optional base URL for API
            
        Returns:
            Dictionary with scan results
        """
        print(f"🔌 Scanning API: {openapi_spec}")
        
        if not self.zap:
            return self._mock_scan_result(openapi_spec, "ZAP not connected")
        
        try:
            # Import OpenAPI definition
            if openapi_spec.startswith('http'):
                self.zap.openapi.import_url(openapi_spec, base_url)
            else:
                self.zap.openapi.import_file(openapi_spec, base_url)
            
            # Run scan on imported API
            target = base_url or openapi_spec
            return self.scan(target, scan_type='full', **kwargs)
            
        except Exception as e:
            print(f"❌ API scan error: {e}")
            return {'error': str(e)}
    
    def full_assessment(self, target: str, include_spider: bool = True,
                       include_active: bool = False, **kwargs) -> Dict:
        """
        Comprehensive security assessment
        
        Args:
            target: Target URL
            include_spider: Include spidering
            include_active: Include active scanning (requires confirmation)
            
        Returns:
            Comprehensive scan results
        """
        print(f"🔐 Starting full security assessment: {target}")
        
        scan_type = 'full' if include_active else 'passive'
        return self.scan(target, scan_type=scan_type, 
                        report_format=['html', 'json', 'xml'], **kwargs)
    
    def _mock_scan_result(self, target: str, reason: str) -> Dict:
        """Return mock scan result when ZAP is not available"""
        return {
            'target': target,
            'scan_type': 'none',
            'scan_start': datetime.now().isoformat(),
            'scan_end': datetime.now().isoformat(),
            'alerts': [],
            'summary': {},
            'error': reason,
            'note': 'This is a mock result. Install and run ZAP for real scanning.'
        }


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    scanner = SecurityScanner()
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
        scan_type = sys.argv[2] if len(sys.argv) > 2 else 'passive'
        
        print(f"🔒 Security Scanner")
        print(f"Target: {target}")
        print(f"Type: {scan_type}")
        print()
        
        results = scanner.scan(target, scan_type=scan_type)
        
        # Save results
        output_file = f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
    else:
        print("Usage: python zap.py <target_url> [scan_type]")
        print("Example: python zap.py https://example.com passive")
        print("Scan types: passive, active, full")