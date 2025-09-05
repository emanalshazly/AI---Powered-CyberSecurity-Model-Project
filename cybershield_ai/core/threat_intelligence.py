"""
Advanced Threat Intelligence System
Real-time threat intelligence gathering and analysis
"""

import asyncio
import logging
import aiohttp
import json
import yaml
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import feedparser
import requests
from bs4 import BeautifulSoup
import re
import hashlib
from collections import defaultdict
import sqlite3

from core.config import settings
from core.ai_engine import AIEngine

logger = logging.getLogger(__name__)

@dataclass
class ThreatIndicator:
    """Threat indicator data structure"""
    id: str
    type: str  # IP, Domain, URL, Hash, Email
    value: str
    confidence: float
    severity: str
    source: str
    first_seen: datetime
    last_seen: datetime
    tags: List[str]
    description: str
    references: List[str]

@dataclass
class ThreatActor:
    """Threat actor information"""
    id: str
    name: str
    aliases: List[str]
    country: Optional[str]
    motivation: str
    capabilities: List[str]
    targets: List[str]
    techniques: List[str]
    last_activity: datetime
    confidence: float

@dataclass
class ThreatCampaign:
    """Threat campaign information"""
    id: str
    name: str
    description: str
    threat_actors: List[str]
    indicators: List[str]
    start_date: datetime
    end_date: Optional[datetime]
    status: str  # active, inactive, resolved
    targets: List[str]
    techniques: List[str]

class ThreatIntelligence:
    """
    Advanced Threat Intelligence System
    Gathers, analyzes, and correlates threat intelligence from multiple sources
    """
    
    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine
        self.indicators = {}
        self.threat_actors = {}
        self.campaigns = {}
        self.monitoring = False
        self.session = None
        
        # Initialize databases
        self._init_databases()
        
        # Load threat intelligence sources
        self._load_threat_sources()
        
        # Initialize correlation engine
        self.correlation_engine = ThreatCorrelationEngine(ai_engine)
    
    def _init_databases(self):
        """Initialize threat intelligence databases"""
        try:
            # Create SQLite database for threat intelligence
            self.db_path = Path("data/threat_intelligence.db")
            self.db_path.parent.mkdir(exist_ok=True)
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threat_indicators (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    value TEXT,
                    confidence REAL,
                    severity TEXT,
                    source TEXT,
                    first_seen TIMESTAMP,
                    last_seen TIMESTAMP,
                    tags TEXT,
                    description TEXT,
                    references TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threat_actors (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    aliases TEXT,
                    country TEXT,
                    motivation TEXT,
                    capabilities TEXT,
                    targets TEXT,
                    last_activity TIMESTAMP,
                    confidence REAL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threat_campaigns (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    threat_actors TEXT,
                    indicators TEXT,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    status TEXT,
                    targets TEXT,
                    techniques TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Threat intelligence databases initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize threat intelligence databases: {e}")
    
    def _load_threat_sources(self):
        """Load threat intelligence sources configuration"""
        try:
            sources_file = Path("data/threat_sources.yaml")
            if sources_file.exists():
                with open(sources_file, 'r') as f:
                    self.threat_sources = yaml.safe_load(f)
            else:
                # Default threat sources
                self.threat_sources = {
                    "feeds": [
                        {
                            "name": "ESET Blog",
                            "url": "https://feeds.feedburner.com/eset/blog",
                            "type": "rss",
                            "enabled": True
                        },
                        {
                            "name": "Malware Traffic Analysis",
                            "url": "https://www.malware-traffic-analysis.net/blog-entries.html",
                            "type": "rss",
                            "enabled": True
                        },
                        {
                            "name": "Bleeping Computer",
                            "url": "https://www.bleepingcomputer.com/feed/",
                            "type": "rss",
                            "enabled": True
                        },
                        {
                            "name": "Krebs on Security",
                            "url": "https://krebsonsecurity.com/feed/",
                            "type": "rss",
                            "enabled": True
                        }
                    ],
                    "apis": [
                        {
                            "name": "VirusTotal",
                            "url": "https://www.virustotal.com/vtapi/v2",
                            "type": "api",
                            "enabled": False  # Requires API key
                        },
                        {
                            "name": "AbuseIPDB",
                            "url": "https://api.abuseipdb.com/api/v2",
                            "type": "api",
                            "enabled": False  # Requires API key
                        }
                    ],
                    "iocs": [
                        {
                            "name": "MISP",
                            "url": "https://misp.example.com",
                            "type": "misp",
                            "enabled": False  # Requires configuration
                        }
                    ]
                }
            
            logger.info("✅ Threat intelligence sources loaded")
            
        except Exception as e:
            logger.error(f"Failed to load threat sources: {e}")
    
    async def start_monitoring(self):
        """Start continuous threat intelligence monitoring"""
        self.monitoring = True
        logger.info("🔄 Starting threat intelligence monitoring...")
        
        # Create aiohttp session
        self.session = aiohttp.ClientSession()
        
        while self.monitoring:
            try:
                # Gather threat intelligence from all sources
                await self._gather_threat_intelligence()
                
                # Perform correlation analysis
                await self._correlate_threats()
                
                # Update threat actor profiles
                await self._update_threat_actors()
                
                # Generate threat intelligence reports
                await self._generate_intelligence_reports()
                
                # Wait for next cycle
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                logger.error(f"Error in threat intelligence monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
        
        # Close session
        if self.session:
            await self.session.close()
    
    async def _gather_threat_intelligence(self):
        """Gather threat intelligence from all configured sources"""
        try:
            logger.info("📡 Gathering threat intelligence...")
            
            # Process RSS feeds
            for feed in self.threat_sources.get("feeds", []):
                if feed.get("enabled", False):
                    await self._process_rss_feed(feed)
            
            # Process API sources
            for api in self.threat_sources.get("apis", []):
                if api.get("enabled", False):
                    await self._process_api_source(api)
            
            # Process IOC sources
            for ioc in self.threat_sources.get("iocs", []):
                if ioc.get("enabled", False):
                    await self._process_ioc_source(ioc)
            
            logger.info("✅ Threat intelligence gathering completed")
            
        except Exception as e:
            logger.error(f"Error gathering threat intelligence: {e}")
    
    async def _process_rss_feed(self, feed_config: Dict[str, Any]):
        """Process RSS feed for threat intelligence"""
        try:
            feed_url = feed_config["url"]
            feed_name = feed_config["name"]
            
            logger.info(f"📰 Processing RSS feed: {feed_name}")
            
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:10]:  # Process last 10 entries
                # Extract threat indicators from entry
                indicators = await self._extract_indicators_from_text(
                    entry.title + " " + entry.get("summary", ""),
                    source=f"RSS:{feed_name}"
                )
                
                # Process each indicator
                for indicator in indicators:
                    await self._process_threat_indicator(indicator)
            
            logger.info(f"✅ Processed RSS feed: {feed_name}")
            
        except Exception as e:
            logger.error(f"Error processing RSS feed {feed_config['name']}: {e}")
    
    async def _process_api_source(self, api_config: Dict[str, Any]):
        """Process API source for threat intelligence"""
        try:
            api_name = api_config["name"]
            api_url = api_config["url"]
            
            logger.info(f"🔌 Processing API source: {api_name}")
            
            # This is a placeholder - in reality, you'd implement specific API calls
            # based on the API type and authentication requirements
            
            if api_name == "VirusTotal":
                await self._process_virustotal_api(api_url)
            elif api_name == "AbuseIPDB":
                await self._process_abuseipdb_api(api_url)
            
            logger.info(f"✅ Processed API source: {api_name}")
            
        except Exception as e:
            logger.error(f"Error processing API source {api_config['name']}: {e}")
    
    async def _process_ioc_source(self, ioc_config: Dict[str, Any]):
        """Process IOC source for threat intelligence"""
        try:
            ioc_name = ioc_config["name"]
            ioc_url = ioc_config["url"]
            
            logger.info(f"🎯 Processing IOC source: {ioc_name}")
            
            # This is a placeholder - in reality, you'd implement specific IOC processing
            # based on the source type (MISP, STIX, etc.)
            
            logger.info(f"✅ Processed IOC source: {ioc_name}")
            
        except Exception as e:
            logger.error(f"Error processing IOC source {ioc_config['name']}: {e}")
    
    async def _extract_indicators_from_text(self, text: str, source: str) -> List[ThreatIndicator]:
        """Extract threat indicators from text using AI and pattern matching"""
        indicators = []
        
        try:
            # Use AI to analyze text for threats
            ai_analysis = await self.ai_engine.detect_threat(text, "threat_intelligence")
            
            # Extract IP addresses
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            ips = re.findall(ip_pattern, text)
            for ip in ips:
                if self._is_valid_ip(ip):
                    indicator = ThreatIndicator(
                        id=hashlib.md5(f"ip:{ip}:{source}".encode()).hexdigest(),
                        type="IP",
                        value=ip,
                        confidence=ai_analysis.get("confidence", 0.5),
                        severity=ai_analysis.get("threat_level", "medium"),
                        source=source,
                        first_seen=datetime.now(),
                        last_seen=datetime.now(),
                        tags=["malicious", "suspicious"],
                        description=f"Malicious IP address found in {source}",
                        references=[]
                    )
                    indicators.append(indicator)
            
            # Extract domains
            domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
            domains = re.findall(domain_pattern, text)
            for domain in domains:
                if self._is_suspicious_domain(domain):
                    indicator = ThreatIndicator(
                        id=hashlib.md5(f"domain:{domain}:{source}".encode()).hexdigest(),
                        type="Domain",
                        value=domain,
                        confidence=0.7,
                        severity="medium",
                        source=source,
                        first_seen=datetime.now(),
                        last_seen=datetime.now(),
                        tags=["malicious", "suspicious"],
                        description=f"Suspicious domain found in {source}",
                        references=[]
                    )
                    indicators.append(indicator)
            
            # Extract URLs
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            urls = re.findall(url_pattern, text)
            for url in urls:
                if self._is_suspicious_url(url):
                    indicator = ThreatIndicator(
                        id=hashlib.md5(f"url:{url}:{source}".encode()).hexdigest(),
                        type="URL",
                        value=url,
                        confidence=0.6,
                        severity="medium",
                        source=source,
                        first_seen=datetime.now(),
                        last_seen=datetime.now(),
                        tags=["malicious", "suspicious"],
                        description=f"Suspicious URL found in {source}",
                        references=[]
                    )
                    indicators.append(indicator)
            
            # Extract file hashes
            hash_patterns = [
                r'\b[a-fA-F0-9]{32}\b',  # MD5
                r'\b[a-fA-F0-9]{40}\b',  # SHA1
                r'\b[a-fA-F0-9]{64}\b'   # SHA256
            ]
            for pattern in hash_patterns:
                hashes = re.findall(pattern, text)
                for hash_value in hashes:
                    indicator = ThreatIndicator(
                        id=hashlib.md5(f"hash:{hash_value}:{source}".encode()).hexdigest(),
                        type="Hash",
                        value=hash_value,
                        confidence=0.8,
                        severity="high",
                        source=source,
                        first_seen=datetime.now(),
                        last_seen=datetime.now(),
                        tags=["malware", "suspicious"],
                        description=f"Malware hash found in {source}",
                        references=[]
                    )
                    indicators.append(indicator)
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error extracting indicators from text: {e}")
            return []
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Check if IP address is valid"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not 0 <= int(part) <= 255:
                    return False
            return True
        except:
            return False
    
    def _is_suspicious_domain(self, domain: str) -> bool:
        """Check if domain is suspicious"""
        suspicious_patterns = [
            r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',  # IP in domain
            r'bit\.ly|tinyurl|t\.co',  # URL shorteners
            r'[a-z0-9]{10,}\.tk|\.ml|\.ga|\.cf',  # Suspicious TLDs
            r'[0-9]{8,}',  # Many numbers
            r'[a-z]{1,3}[0-9]{5,}',  # Short letters + many numbers
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, domain, re.IGNORECASE):
                return True
        return False
    
    def _is_suspicious_url(self, url: str) -> bool:
        """Check if URL is suspicious"""
        suspicious_patterns = [
            r'bit\.ly|tinyurl|t\.co',  # URL shorteners
            r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',  # IP addresses
            r'[a-z0-9]{10,}\.tk|\.ml|\.ga|\.cf',  # Suspicious TLDs
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    async def _process_threat_indicator(self, indicator: ThreatIndicator):
        """Process a threat indicator"""
        try:
            # Check if indicator already exists
            existing = self.indicators.get(indicator.id)
            if existing:
                # Update existing indicator
                existing.last_seen = datetime.now()
                existing.confidence = max(existing.confidence, indicator.confidence)
                existing.tags = list(set(existing.tags + indicator.tags))
            else:
                # Add new indicator
                self.indicators[indicator.id] = indicator
            
            # Save to database
            await self._save_threat_indicator(indicator)
            
        except Exception as e:
            logger.error(f"Error processing threat indicator: {e}")
    
    async def _save_threat_indicator(self, indicator: ThreatIndicator):
        """Save threat indicator to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO threat_indicators 
                (id, type, value, confidence, severity, source, first_seen, last_seen, 
                 tags, description, references)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                indicator.id, indicator.type, indicator.value, indicator.confidence,
                indicator.severity, indicator.source, indicator.first_seen.isoformat(),
                indicator.last_seen.isoformat(), json.dumps(indicator.tags),
                indicator.description, json.dumps(indicator.references)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save threat indicator: {e}")
    
    async def _correlate_threats(self):
        """Correlate threats and identify patterns"""
        try:
            logger.info("🔍 Correlating threats...")
            
            # Use correlation engine
            correlations = await self.correlation_engine.analyze_correlations(self.indicators)
            
            # Process correlations
            for correlation in correlations:
                await self._process_correlation(correlation)
            
            logger.info("✅ Threat correlation completed")
            
        except Exception as e:
            logger.error(f"Error correlating threats: {e}")
    
    async def _process_correlation(self, correlation: Dict[str, Any]):
        """Process a threat correlation"""
        try:
            # This would process correlations and potentially create new threat campaigns
            # or update existing ones
            pass
            
        except Exception as e:
            logger.error(f"Error processing correlation: {e}")
    
    async def _update_threat_actors(self):
        """Update threat actor profiles"""
        try:
            logger.info("👤 Updating threat actor profiles...")
            
            # This would analyze indicators to identify and update threat actors
            # For now, we'll implement a basic version
            
            # Group indicators by common characteristics
            actor_indicators = defaultdict(list)
            for indicator in self.indicators.values():
                # Simple grouping by source and tags
                key = f"{indicator.source}:{':'.join(indicator.tags)}"
                actor_indicators[key].append(indicator)
            
            # Create or update threat actors
            for key, indicators in actor_indicators.items():
                if len(indicators) > 3:  # Minimum indicators for actor
                    await self._create_or_update_threat_actor(key, indicators)
            
            logger.info("✅ Threat actor profiles updated")
            
        except Exception as e:
            logger.error(f"Error updating threat actors: {e}")
    
    async def _create_or_update_threat_actor(self, key: str, indicators: List[ThreatIndicator]):
        """Create or update a threat actor profile"""
        try:
            actor_id = hashlib.md5(key.encode()).hexdigest()
            
            # Analyze indicators to determine actor characteristics
            sources = list(set(indicator.source for indicator in indicators))
            tags = list(set(tag for indicator in indicators for tag in indicator.tags))
            
            # Create threat actor
            actor = ThreatActor(
                id=actor_id,
                name=f"Threat Actor {actor_id[:8]}",
                aliases=[],
                country=None,
                motivation="Unknown",
                capabilities=tags,
                targets=[],
                techniques=[],
                last_activity=max(indicator.last_seen for indicator in indicators),
                confidence=sum(indicator.confidence for indicator in indicators) / len(indicators)
            )
            
            self.threat_actors[actor_id] = actor
            
            # Save to database
            await self._save_threat_actor(actor)
            
        except Exception as e:
            logger.error(f"Error creating/updating threat actor: {e}")
    
    async def _save_threat_actor(self, actor: ThreatActor):
        """Save threat actor to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO threat_actors 
                (id, name, aliases, country, motivation, capabilities, targets, 
                 last_activity, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                actor.id, actor.name, json.dumps(actor.aliases), actor.country,
                actor.motivation, json.dumps(actor.capabilities), json.dumps(actor.targets),
                actor.last_activity.isoformat(), actor.confidence
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save threat actor: {e}")
    
    async def _generate_intelligence_reports(self):
        """Generate threat intelligence reports"""
        try:
            logger.info("📊 Generating threat intelligence reports...")
            
            # Generate daily summary
            await self._generate_daily_summary()
            
            # Generate threat actor report
            await self._generate_threat_actor_report()
            
            # Generate indicator report
            await self._generate_indicator_report()
            
            logger.info("✅ Threat intelligence reports generated")
            
        except Exception as e:
            logger.error(f"Error generating intelligence reports: {e}")
    
    async def _generate_daily_summary(self):
        """Generate daily threat intelligence summary"""
        try:
            # Count indicators by type
            indicator_counts = defaultdict(int)
            for indicator in self.indicators.values():
                indicator_counts[indicator.type] += 1
            
            # Count by severity
            severity_counts = defaultdict(int)
            for indicator in self.indicators.values():
                severity_counts[indicator.severity] += 1
            
            summary = {
                "date": datetime.now().isoformat(),
                "total_indicators": len(self.indicators),
                "indicator_counts": dict(indicator_counts),
                "severity_counts": dict(severity_counts),
                "threat_actors": len(self.threat_actors),
                "campaigns": len(self.campaigns)
            }
            
            # Save summary
            summary_file = Path(f"reports/daily_summary_{datetime.now().strftime('%Y%m%d')}.json")
            summary_file.parent.mkdir(exist_ok=True)
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
    
    async def _generate_threat_actor_report(self):
        """Generate threat actor report"""
        try:
            # This would generate a detailed threat actor report
            pass
            
        except Exception as e:
            logger.error(f"Error generating threat actor report: {e}")
    
    async def _generate_indicator_report(self):
        """Generate indicator report"""
        try:
            # This would generate a detailed indicator report
            pass
            
        except Exception as e:
            logger.error(f"Error generating indicator report: {e}")
    
    async def get_threat_intelligence_summary(self) -> Dict[str, Any]:
        """Get threat intelligence summary"""
        try:
            return {
                "total_indicators": len(self.indicators),
                "total_threat_actors": len(self.threat_actors),
                "total_campaigns": len(self.campaigns),
                "monitoring_status": "active" if self.monitoring else "inactive",
                "last_update": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting threat intelligence summary: {e}")
            return {"error": str(e)}
    
    def stop_monitoring(self):
        """Stop threat intelligence monitoring"""
        self.monitoring = False
        logger.info("🛑 Stopped threat intelligence monitoring")


class ThreatCorrelationEngine:
    """Advanced threat correlation engine"""
    
    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine
    
    async def analyze_correlations(self, indicators: Dict[str, ThreatIndicator]) -> List[Dict[str, Any]]:
        """Analyze correlations between threat indicators"""
        correlations = []
        
        try:
            # Group indicators by type
            by_type = defaultdict(list)
            for indicator in indicators.values():
                by_type[indicator.type].append(indicator)
            
            # Find correlations within each type
            for indicator_type, type_indicators in by_type.items():
                type_correlations = await self._find_type_correlations(indicator_type, type_indicators)
                correlations.extend(type_correlations)
            
            # Find cross-type correlations
            cross_correlations = await self._find_cross_type_correlations(indicators)
            correlations.extend(cross_correlations)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error analyzing correlations: {e}")
            return []
    
    async def _find_type_correlations(self, indicator_type: str, indicators: List[ThreatIndicator]) -> List[Dict[str, Any]]:
        """Find correlations within a specific indicator type"""
        correlations = []
        
        try:
            if indicator_type == "IP":
                # Find IPs from same subnet
                subnets = defaultdict(list)
                for indicator in indicators:
                    ip_parts = indicator.value.split('.')
                    subnet = '.'.join(ip_parts[:3])
                    subnets[subnet].append(indicator)
                
                for subnet, subnet_indicators in subnets.items():
                    if len(subnet_indicators) > 1:
                        correlations.append({
                            "type": "subnet_correlation",
                            "description": f"Multiple malicious IPs from subnet {subnet}.0/24",
                            "indicators": [ind.id for ind in subnet_indicators],
                            "confidence": 0.8
                        })
            
            elif indicator_type == "Domain":
                # Find domains with similar patterns
                patterns = defaultdict(list)
                for indicator in indicators:
                    domain = indicator.value
                    # Extract pattern (e.g., first part of domain)
                    pattern = domain.split('.')[0] if '.' in domain else domain
                    patterns[pattern].append(indicator)
                
                for pattern, pattern_indicators in patterns.items():
                    if len(pattern_indicators) > 1:
                        correlations.append({
                            "type": "domain_pattern_correlation",
                            "description": f"Multiple domains with similar pattern: {pattern}",
                            "indicators": [ind.id for ind in pattern_indicators],
                            "confidence": 0.7
                        })
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error finding type correlations: {e}")
            return []
    
    async def _find_cross_type_correlations(self, indicators: Dict[str, ThreatIndicator]) -> List[Dict[str, Any]]:
        """Find correlations across different indicator types"""
        correlations = []
        
        try:
            # Find IP-Domain correlations
            ip_indicators = [ind for ind in indicators.values() if ind.type == "IP"]
            domain_indicators = [ind for ind in indicators.values() if ind.type == "Domain"]
            
            for ip_ind in ip_indicators:
                for domain_ind in domain_indicators:
                    # Check if IP and domain are related (simplified check)
                    if self._are_related_indicators(ip_ind, domain_ind):
                        correlations.append({
                            "type": "ip_domain_correlation",
                            "description": f"IP {ip_ind.value} and domain {domain_ind.value} are related",
                            "indicators": [ip_ind.id, domain_ind.id],
                            "confidence": 0.6
                        })
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error finding cross-type correlations: {e}")
            return []
    
    def _are_related_indicators(self, indicator1: ThreatIndicator, indicator2: ThreatIndicator) -> bool:
        """Check if two indicators are related"""
        try:
            # Simple relationship check based on common tags and sources
            common_tags = set(indicator1.tags) & set(indicator2.tags)
            common_sources = indicator1.source == indicator2.source
            
            return len(common_tags) > 0 or common_sources
            
        except Exception:
            return False