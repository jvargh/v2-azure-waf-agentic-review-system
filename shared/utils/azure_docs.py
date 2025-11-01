"""
Azure documentation search utilities.
"""

import asyncio
import aiohttp
import logging
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime, timedelta
import json

from ..models import AzureDocReference

logger = logging.getLogger(__name__)


class AzureDocsSearcher:
    """Searches Microsoft Learn for Azure documentation."""
    
    def __init__(self, cache_ttl_hours: int = 24):
        self.cache_ttl_hours = cache_ttl_hours
        self.cache_dir = "cache/azure_docs"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Common search queries for reliability
        self.reliability_queries = [
            "Azure Well-Architected reliability design principles",
            "Azure reliability checklist",
            "Azure reliability tradeoffs",
            "Azure reliability monitoring alerting strategy",
            "Azure zone redundant deployment",
            "Azure disaster recovery best practices",
            "Azure backup and restore strategies"
        ]
    
    async def search_reliability_docs(self, 
                                    service_names: Optional[List[str]] = None) -> List[AzureDocReference]:
        """Search for reliability documentation, optionally including service-specific guidance."""
        all_docs = []
        
        # Search general reliability docs
        for query in self.reliability_queries:
            docs = await self._search_microsoft_learn(query)
            all_docs.extend(docs)
        
        # Search service-specific reliability docs
        if service_names:
            for service in service_names:
                service_query = f'"{service}" reliability site:learn.microsoft.com'
                docs = await self._search_microsoft_learn(service_query)
                all_docs.extend(docs)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_docs = []
        for doc in all_docs:
            if doc.url not in seen_urls:
                seen_urls.add(doc.url)
                unique_docs.append(doc)
        
        return unique_docs[:10]  # Return top 10 most relevant
    
    async def _search_microsoft_learn(self, query: str) -> List[AzureDocReference]:
        """Perform web search for Microsoft Learn content."""
        cache_key = self._get_cache_key(query)
        
        # Check cache first
        cached_results = self._get_cached_results(cache_key)
        if cached_results:
            return cached_results
        
        try:
            # Use web search (in production, you might use Bing Search API)
            search_url = f"https://www.bing.com/search?q={quote_plus(query + ' site:learn.microsoft.com')}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }) as response:
                    if response.status == 200:
                        html = await response.text()
                        results = self._parse_search_results(html)
                        
                        # Fetch content for top results
                        docs = []
                        for result in results[:3]:  # Top 3 results
                            doc_content = await self._fetch_page_content(result['url'])
                            if doc_content:
                                doc = AzureDocReference(
                                    title=result['title'],
                                    url=result['url'],
                                    content_excerpt=result['snippet'],
                                    full_content=doc_content,
                                    relevance_score=result.get('relevance', 1.0)
                                )
                                docs.append(doc)
                        
                        # Cache results
                        self._cache_results(cache_key, docs)
                        return docs
                        
        except Exception as e:
            logger.error(f"Error searching Microsoft Learn: {e}")
            # Fallback to hardcoded reliable sources
            return await self._get_fallback_docs(query)
        
        return []
    
    def _parse_search_results(self, html: str) -> List[Dict[str, str]]:
        """Parse search results from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Parse Bing search results
        for result in soup.find_all('li', class_='b_algo'):
            title_elem = result.find('h2')
            if title_elem and title_elem.find('a'):
                title = title_elem.get_text().strip()
                url = title_elem.find('a')['href']
                
                # Only include learn.microsoft.com URLs
                if 'learn.microsoft.com' in url:
                    snippet_elem = result.find('p')
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet,
                        'relevance': 1.0
                    })
        
        return results
    
    async def _fetch_page_content(self, url: str) -> Optional[str]:
        """Fetch full content from a Microsoft Learn page."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract main content
                        main_content = soup.find('div', {'data-bi-name': 'content'})
                        if main_content:
                            # Remove script and style elements
                            for script in main_content(["script", "style"]):
                                script.decompose()
                            
                            # Get text content
                            text = main_content.get_text()
                            # Clean up whitespace
                            lines = (line.strip() for line in text.splitlines())
                            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                            text = ' '.join(chunk for chunk in chunks if chunk)
                            
                            return text[:5000]  # Limit to 5000 characters
                            
        except Exception as e:
            logger.error(f"Error fetching page content from {url}: {e}")
        
        return None
    
    async def _get_fallback_docs(self, query: str) -> List[AzureDocReference]:
        """Get fallback documentation when search fails."""
        fallback_docs = [
            AzureDocReference(
                title="Design principles for Azure applications",
                url="https://learn.microsoft.com/en-us/azure/well-architected/reliability/principles",
                content_excerpt="Design principles that serve as a compass for subsequent design decisions across the critical design areas for reliability."
            ),
            AzureDocReference(
                title="Reliability checklist",
                url="https://learn.microsoft.com/en-us/azure/well-architected/reliability/checklist",
                content_excerpt="Checklist for reliability pillar with design considerations and recommendations."
            ),
            AzureDocReference(
                title="Reliability design patterns",
                url="https://learn.microsoft.com/en-us/azure/well-architected/reliability/design-patterns",
                content_excerpt="Design patterns for building reliable applications on Azure."
            )
        ]
        return fallback_docs
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query."""
        import hashlib
        return hashlib.md5(query.encode()).hexdigest()
    
    def _get_cached_results(self, cache_key: str) -> Optional[List[AzureDocReference]]:
        """Get cached search results if still valid."""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if cache is still valid
                cache_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cache_time < timedelta(hours=self.cache_ttl_hours):
                    return [AzureDocReference(**doc) for doc in cached_data['docs']]
                    
            except Exception as e:
                logger.error(f"Error reading cache file {cache_file}: {e}")
        
        return None
    
    def _cache_results(self, cache_key: str, docs: List[AzureDocReference]) -> None:
        """Cache search results."""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'docs': [doc.dict() for doc in docs]
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error writing cache file {cache_file}: {e}")