#!/usr/bin/env python3
"""
Universal Job Scraper for Greenhouse-powered career pages
Adapted from OpenAI and Anthropic scrapers
"""

import asyncio
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TalentScraper:
    """Universal scraper for multiple job board providers (Greenhouse, Ashby, etc.)"""

    def __init__(self):
        self.browser = None
        self.context = None

    def detect_provider(self, url: str) -> str:
        """Detect which job board provider is being used"""
        if 'greenhouse.io' in url:
            return 'greenhouse'
        elif 'ashbyhq.com' in url:
            return 'ashby'
        elif 'stripe.com/jobs' in url:
            return 'stripe'
        elif 'databricks.com' in url:
            return 'databricks'
        elif 'lifeatcanva.com' in url or 'canva.com' in url:
            return 'canva'
        elif 'rippling.com' in url or 'ats.rippling.com' in url:
            return 'rippling'
        elif 'lever.co' in url:
            return 'lever'
        elif 'workable.com' in url:
            return 'workable'
        else:
            # Default to greenhouse strategy for unknown providers
            return 'unknown'

    async def initialize(self):
        """Initialize the browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()

    def extract_salary(self, text: str) -> Optional[Dict[str, any]]:
        """Extract salary information from text"""
        if not text:
            return None

        # Try different salary patterns
        # Pattern 1: $XXXk - $XXXk
        match = re.search(r'\$(\d{1,3})[Kk]\s*[-–—]\s*\$(\d{1,3})[Kk]', text)
        if match:
            return {
                'min': int(float(match.group(1)) * 1000),
                'max': int(float(match.group(2)) * 1000),
                'raw': match.group(0)
            }

        # Pattern 2: $XXX,XXX - $XXX,XXX (with or without spaces around dash)
        match = re.search(r'\$(\d{1,3}(?:,\d{3})*)\s*[-–—]\s*\$(\d{1,3}(?:,\d{3})*)', text)
        if match:
            min_sal = match.group(1).replace(',', '')
            max_sal = match.group(2).replace(',', '')
            # Check if these are unrealistically low values (likely hourly or missing 'k')
            min_val = int(min_sal)
            max_val = int(max_sal)
            # If values are under 1000 and appear to be hourly rates, multiply by 1000 (assume 'k')
            if min_val < 1000 and max_val < 1000 and 'per hour' in text.lower():
                # This is hourly rate, keep as is
                pass
            elif min_val < 1000 and max_val < 1000:
                # Likely missing 'k', multiply by 1000
                min_val *= 1000
                max_val *= 1000
            return {
                'min': min_val,
                'max': max_val,
                'raw': match.group(0)
            }

        # Pattern 3: $XXX,XXX to $XXX,XXX
        match = re.search(r'\$(\d{1,3}(?:,\d{3})*)\s*to\s*\$(\d{1,3}(?:,\d{3})*)', text)
        if match:
            min_sal = match.group(1).replace(',', '')
            max_sal = match.group(2).replace(',', '')
            return {
                'min': int(min_sal),
                'max': int(max_sal),
                'raw': match.group(0)
            }

        # Pattern 4: $XXX,XXX per year (single value, common in Notion)
        match = re.search(r'\$(\d{1,3}(?:,\d{3})*)\s*(?:per year|annually|/year|\/yr)', text, re.IGNORECASE)
        if match:
            salary_val = int(match.group(1).replace(',', ''))
            # For single values, create a range around it (±10%)
            return {
                'min': int(salary_val * 0.9),
                'max': int(salary_val * 1.1),
                'raw': match.group(0)
            }

        # Pattern 5: XXX,XXX - XXX,XXX USD/per year
        match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*[-–—]\s*(\d{1,3}(?:,\d{3})*)\s*(?:USD|per year|annually)', text, re.IGNORECASE)
        if match:
            min_sal = match.group(1).replace(',', '')
            max_sal = match.group(2).replace(',', '')
            return {
                'min': int(min_sal),
                'max': int(max_sal),
                'raw': match.group(0)
            }

        # Pattern 5: XXX-XXXk
        match = re.search(r'(\d{1,3})\s*[-–—]\s*(\d{1,3})[Kk]', text)
        if match:
            return {
                'min': int(float(match.group(1)) * 1000),
                'max': int(float(match.group(2)) * 1000),
                'raw': match.group(0)
            }

        # Pattern 6: Compensation/Salary: text with numbers
        match = re.search(r'(?:compensation|salary|pay)[:\s]+.*?(\d{2,3})[Kk]', text, re.IGNORECASE)
        if match:
            amount = int(float(match.group(1)) * 1000)
            return {
                'min': amount,
                'max': amount,
                'raw': match.group(0)
            }

        return None

    async def scrape_jobs(self, company_url: str, fetch_details: bool = True, max_detail_fetches: int = 20) -> List[Dict]:
        """Universal job scraper that routes to the appropriate provider-specific scraper"""
        provider = self.detect_provider(company_url)
        logger.info(f"Detected provider: {provider} for URL: {company_url}")

        if provider == 'ashby':
            return await self.scrape_ashby_jobs(company_url, fetch_details, max_detail_fetches)
        elif provider == 'stripe':
            return await self.scrape_stripe_jobs(company_url, fetch_details, max_detail_fetches)
        elif provider == 'databricks':
            return await self.scrape_databricks_jobs(company_url, fetch_details, max_detail_fetches)
        elif provider == 'canva':
            return await self.scrape_canva_jobs(company_url, fetch_details, max_detail_fetches)
        elif provider == 'rippling':
            return await self.scrape_rippling_jobs(company_url, fetch_details, max_detail_fetches)
        else:
            # Default to Greenhouse strategy for greenhouse and unknown providers
            return await self.scrape_greenhouse_jobs(company_url, fetch_details, max_detail_fetches)

    async def scrape_ashby_jobs(self, company_url: str, fetch_details: bool = True, max_detail_fetches: int = 20) -> List[Dict]:
        """Scrape jobs from an Ashby-powered careers page"""
        page = await self.context.new_page()
        jobs = []

        try:
            logger.info(f"Scraping Ashby site: {company_url}")
            await page.goto(company_url, wait_until='domcontentloaded', timeout=30000)

            # Ashby sites often load content dynamically, wait for it
            await page.wait_for_timeout(5000)

            # Some Ashby sites require scrolling to load all jobs
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)

            # Ashby-specific selectors - more comprehensive
            job_selectors = [
                '[data-testid="job-board-job-card"]',  # Ashby's test ID
                '.ashby-job-posting-item',
                '.ashby-job-posting-title',
                'div[role="listitem"]',
                'a[href*="/openai/"]',  # Links containing company name
                'a[href^="/"]',  # All relative links
                '.job-card',
                '.posting',
                '.job-posting',
                'div[class*="JobCard"]',
                'div[class*="job-card"]',
                'article',
                '[data-qa="job-card"]',
                'h3 > a',  # Links inside h3 headers
                'h4 > a',  # Links inside h4 headers
            ]

            # Extract company name from URL for dynamic matching
            company_name = company_url.split('/')[-1] if '/' in company_url else 'jobs'

            job_elements = None
            for selector in job_selectors:
                job_elements = await page.query_selector_all(selector)
                if job_elements and len(job_elements) > 0:
                    # Filter out non-job elements
                    valid_elements = []
                    for elem in job_elements:
                        text = await elem.text_content()
                        href = await elem.get_attribute('href') if await elem.evaluate('el => el.tagName === "A"') else None

                        # Check if it's a job link
                        if text and len(text.strip()) > 5:
                            if href and (f'/{company_name}/' in href or href.startswith(f'/{company_name}/')):
                                valid_elements.append(elem)
                            elif not href and not any(skip in text.lower() for skip in ['cookie', 'privacy', 'terms', 'careers at']):
                                valid_elements.append(elem)

                    if valid_elements:
                        job_elements = valid_elements
                        logger.info(f"Found {len(job_elements)} jobs using Ashby selector: {selector}")
                        break

            if not job_elements:
                # Try to find job listings in the main content
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # Look for links that contain the company name or /jobs/ in the href
                job_links = []
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link['href']
                    text = link.get_text(strip=True)
                    # Check if it's likely a job link
                    if text and len(text) > 5 and (
                        f'/{company_name}/' in href or
                        href.startswith(f'/{company_name}/') or
                        '/jobs/' in href
                    ) and not any(skip in text.lower() for skip in ['cookie', 'privacy', 'terms', 'careers']):
                        job_links.append(link)

                if job_links:
                    logger.info(f"Found {len(job_links)} job links via href pattern")
                    for link in job_links:
                        job = await self.parse_ashby_job_link(link, page)
                        if job:
                            jobs.append(job)
                    return jobs

            # Parse job elements
            detail_fetch_count = 0
            for i, element in enumerate(job_elements):
                try:
                    job = await self.parse_ashby_job_element(element, page)
                    if job:
                        # For Notion specifically, always try to fetch details for salary
                        # Since Notion puts salary info in job descriptions
                        is_notion = 'notion' in company_url.lower()

                        # Try to get salary from job detail page if not found
                        if fetch_details and job.get('url') and detail_fetch_count < max_detail_fetches:
                            # For Notion, always fetch details; for others, only if no salary found
                            if is_notion or not job.get('salary'):
                                try:
                                    logger.info(f"Fetching details for Ashby job {i+1}/{len(job_elements)}: {job['title'][:30]}...")
                                    details = await self.scrape_job_details(job['url'])
                                    if details.get('salary'):
                                        job['salary'] = details['salary']
                                        logger.info(f"Found salary: ${details['salary']['min']:,} - ${details['salary']['max']:,}")
                                    elif is_notion:
                                        logger.info(f"No salary found for Notion job: {job['title'][:30]}")
                                    detail_fetch_count += 1
                                except Exception as e:
                                    logger.debug(f"Could not fetch job details: {e}")
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing Ashby job element: {e}")
                    continue

            logger.info(f"Scraped {len(jobs)} jobs from Ashby site: {company_url}")

        except Exception as e:
            logger.error(f"Error scraping Ashby site {company_url}: {e}")
        finally:
            await page.close()

        return jobs

    async def parse_ashby_job_element(self, element, page) -> Optional[Dict]:
        """Parse a single Ashby job element"""
        try:
            # Get full text and HTML
            full_text = await element.text_content()
            if not full_text:
                return None

            html = await element.inner_html()
            soup = BeautifulSoup(html, 'html.parser')

            # Get job title - Ashby often uses h3 or strong tags
            title = None
            title_elem = soup.find(['h3', 'h4', 'h2', 'strong'])
            if title_elem:
                title = title_elem.get_text(strip=True)
            else:
                # Try to find the first link text
                link = soup.find('a')
                if link:
                    title = link.get_text(strip=True)

            if not title:
                # Get first non-empty line
                lines = [line.strip() for line in full_text.strip().split('\n') if line.strip()]
                if lines:
                    title = lines[0]

            if not title:
                return None

            # Get job URL
            url = None

            # First check if the element itself has an href attribute (for Ashby)
            element_href = await element.get_attribute('href')
            if element_href:
                url = element_href
                if url and not url.startswith('http'):
                    # For Ashby, construct full URL properly
                    if 'ashbyhq.com' in page.url:
                        # Get the base URL (e.g., https://jobs.ashbyhq.com)
                        parsed_url = page.url.split('/')
                        base_url = '/'.join(parsed_url[:3])  # Gets https://jobs.ashbyhq.com
                        # Add the company name if the URL doesn't have it
                        if '/notion' not in url and 'notion' in page.url.lower():
                            url = f"{base_url}/notion{url}" if url.startswith('/') else f"{base_url}/notion/{url}"
                        else:
                            url = f"{base_url}{url}" if url.startswith('/') else f"{base_url}/{url}"
                    else:
                        base_url = page.url.split('/jobs')[0]
                        url = f"{base_url}{url}" if url.startswith('/') else f"{base_url}/{url}"
            else:
                # Otherwise look for a link within the element
                link = soup.find('a', href=True)
                if link:
                    url = link['href']
                    if url and not url.startswith('http'):
                        if 'ashbyhq.com' in page.url:
                            # Get the base URL (e.g., https://jobs.ashbyhq.com)
                            parsed_url = page.url.split('/')
                            base_url = '/'.join(parsed_url[:3])  # Gets https://jobs.ashbyhq.com
                            # Add the company name if the URL doesn't have it
                            if '/notion' not in url and 'notion' in page.url.lower():
                                url = f"{base_url}/notion{url}" if url.startswith('/') else f"{base_url}/notion/{url}"
                            else:
                                url = f"{base_url}{url}" if url.startswith('/') else f"{base_url}/{url}"
                        else:
                            base_url = page.url.split('/jobs')[0]
                            url = f"{base_url}{url}" if url.startswith('/') else f"{base_url}/{url}"

            # Parse location - Ashby often shows it as a separate element
            location = None
            # Look for location patterns
            location_patterns = [
                r'📍\s*([^•\n]+)',  # Location with pin emoji
                r'Location:\s*([^•\n]+)',
                r'•\s*([^•]+)\s*•',  # Between bullet points
            ]

            for pattern in location_patterns:
                match = re.search(pattern, full_text)
                if match:
                    location = match.group(1).strip()
                    break

            if not location:
                # Look for location in specific elements
                for elem in soup.find_all(['span', 'div', 'p']):
                    text = elem.get_text(strip=True)
                    if text and len(text) < 100:
                        lower_text = text.lower()
                        if any(loc in lower_text for loc in ['remote', 'hybrid', 'on-site', 'onsite']) or \
                           any(city in lower_text for city in ['new york', 'san francisco', 'london', 'seattle', 'austin']):
                            location = text
                            break

            # Parse department - Ashby often includes this in the listing
            department = None
            dept_patterns = [
                r'Department:\s*([^•\n]+)',
                r'Team:\s*([^•\n]+)',
            ]

            for pattern in dept_patterns:
                match = re.search(pattern, full_text)
                if match:
                    department = match.group(1).strip()
                    break

            if not department:
                # Try to extract from job title
                title_lower = title.lower()
                if 'engineer' in title_lower or 'developer' in title_lower:
                    department = 'Engineering'
                elif 'product' in title_lower:
                    department = 'Product'
                elif 'design' in title_lower:
                    department = 'Design'
                elif 'sales' in title_lower or 'account' in title_lower:
                    department = 'Sales'
                elif 'marketing' in title_lower or 'growth' in title_lower:
                    department = 'Marketing'
                elif 'data' in title_lower or 'analyst' in title_lower:
                    department = 'Data & Analytics'
                else:
                    department = 'Not specified'

            # Get salary info
            salary_info = self.extract_salary(full_text)

            return {
                'title': title.strip(),
                'url': url,
                'location': location.strip() if location else 'Not specified',
                'department': department.strip() if department else 'Not specified',
                'salary': salary_info,
                'provider': 'ashby',
                'scraped_at': datetime.now().isoformat(),
                'raw_text': full_text
            }

        except Exception as e:
            logger.error(f"Error parsing Ashby job element: {e}")
            return None

    async def parse_ashby_job_link(self, link_soup, page) -> Optional[Dict]:
        """Parse an Ashby job from a link element"""
        try:
            title = link_soup.get_text(strip=True)
            if not title:
                return None

            url = link_soup.get('href', '')
            if url and not url.startswith('http'):
                base_url = page.url.split('/jobs')[0]
                url = f"{base_url}{url}" if url.startswith('/') else f"{base_url}/{url}"

            # Try to get more info from parent or siblings
            parent = link_soup.parent
            full_text = parent.get_text(strip=True) if parent else title

            # Extract location if present
            location = 'Not specified'
            location_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,\s*[A-Z]{2})?)', full_text)
            if location_match:
                potential_loc = location_match.group(1)
                if any(city in potential_loc.lower() for city in ['remote', 'york', 'francisco', 'london', 'seattle']):
                    location = potential_loc

            # Extract department from title
            department = 'Not specified'
            title_lower = title.lower()
            if 'engineer' in title_lower or 'developer' in title_lower:
                department = 'Engineering'
            elif 'product' in title_lower:
                department = 'Product'
            elif 'design' in title_lower:
                department = 'Design'
            elif 'sales' in title_lower:
                department = 'Sales'
            elif 'marketing' in title_lower:
                department = 'Marketing'

            return {
                'title': title,
                'url': url,
                'location': location,
                'department': department,
                'salary': None,
                'provider': 'ashby',
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing Ashby job link: {e}")
            return None

    async def scrape_canva_jobs(self, company_url: str, fetch_details: bool = True, max_detail_fetches: int = 20) -> List[Dict]:
        """Scrape jobs from Canva's custom job board at lifeatcanva.com"""
        page = await self.context.new_page()
        jobs = []

        try:
            logger.info(f"Scraping Canva site: {company_url}")
            await page.goto(company_url, wait_until='domcontentloaded', timeout=30000)

            # Wait for dynamic content to load
            await page.wait_for_timeout(5000)

            # Scroll to load all jobs
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)

            # Canva-specific selectors
            job_selectors = [
                'a[href*="/jobs/"]',  # Job links
                '.job-card',
                '.job-listing',
                '.opportunity',
                '.position',
                'div[class*="JobCard"]',
                'div[class*="jobCard"]',
                'article[class*="job"]',
                '[data-testid="job-card"]',
                '[role="listitem"] a',
                '.careers-opportunity',
                'div[class*="opportunity"]',
                'a[class*="opportunity"]',
                'h3 > a',  # Job titles in headers
                'h4 > a',
                '.role-card',
                'div[class*="role"]'
            ]

            job_elements = None
            for selector in job_selectors:
                job_elements = await page.query_selector_all(selector)
                if job_elements and len(job_elements) > 0:
                    # Filter out non-job elements
                    valid_elements = []
                    for elem in job_elements:
                        text = await elem.text_content()
                        if text and len(text.strip()) > 5 and not any(skip in text.lower() for skip in ['cookie', 'privacy', 'terms', 'careers at', 'benefits', 'perks', 'about']):
                            valid_elements.append(elem)

                    if valid_elements:
                        job_elements = valid_elements
                        logger.info(f"Found {len(job_elements)} jobs using Canva selector: {selector}")
                        break

            if not job_elements:
                # Try to find job links by pattern in HTML
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                job_links = []
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link['href']
                    text = link.get_text(strip=True)
                    # Check if it's likely a job link
                    if text and len(text) > 5 and (
                        '/jobs/' in href or
                        'job-' in href or
                        'position-' in href or
                        'role-' in href
                    ) and not any(skip in text.lower() for skip in ['cookie', 'privacy', 'terms', 'careers', 'benefits']):
                        job_links.append(link)

                if job_links:
                    logger.info(f"Found {len(job_links)} job links via href pattern")
                    for link in job_links:
                        job = await self.parse_canva_job_link(link, page)
                        if job:
                            jobs.append(job)
                    return jobs

            # Parse job elements
            detail_fetch_count = 0
            for i, element in enumerate(job_elements):
                try:
                    job = await self.parse_canva_job_element(element, page)
                    if job:
                        # Try to get salary from job detail page if not found
                        if fetch_details and job.get('url') and not job.get('salary') and detail_fetch_count < max_detail_fetches:
                            try:
                                logger.info(f"Fetching details for Canva job {i+1}/{len(job_elements)}: {job['title'][:30]}...")
                                details = await self.scrape_job_details(job['url'])
                                if details.get('salary'):
                                    job['salary'] = details['salary']
                                    logger.info(f"Found salary: ${details['salary']['min']:,} - ${details['salary']['max']:,}")
                                detail_fetch_count += 1
                            except Exception as e:
                                logger.debug(f"Could not fetch job details: {e}")
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing Canva job element: {e}")
                    continue

            logger.info(f"Scraped {len(jobs)} jobs from Canva site: {company_url}")

        except Exception as e:
            logger.error(f"Error scraping Canva site {company_url}: {e}")
        finally:
            await page.close()

        return jobs

    async def parse_canva_job_element(self, element, page) -> Optional[Dict]:
        """Parse a single Canva job element"""
        try:
            # Get full text and HTML
            full_text = await element.text_content()
            if not full_text:
                return None

            html = await element.inner_html()
            soup = BeautifulSoup(html, 'html.parser')

            # Get job title
            title = None
            title_elem = soup.find(['h3', 'h4', 'h2', 'strong'])
            if title_elem:
                title = title_elem.get_text(strip=True)
            else:
                # Try to find the first link text
                link = soup.find('a')
                if link:
                    title = link.get_text(strip=True)

            if not title:
                # Get first non-empty line
                lines = [line.strip() for line in full_text.strip().split('\n') if line.strip()]
                if lines:
                    title = lines[0]

            if not title:
                return None

            # Clean the job title (remove location if in parentheses)
            location = "Not specified"
            if '(' in title and ')' in title:
                # Extract location from parentheses
                match = re.search(r'\(([^)]+)\)', title)
                if match:
                    location = match.group(1).strip()
                    title = title.replace(match.group(0), '').strip()

            # Get job URL
            url = None
            element_href = await element.get_attribute('href')
            if element_href:
                url = element_href
                if url and not url.startswith('http'):
                    # Construct full URL
                    base_url = 'https://www.lifeatcanva.com'
                    url = f"{base_url}{url}" if url.startswith('/') else f"{base_url}/{url}"
            else:
                # Look for a link within the element
                link = soup.find('a', href=True)
                if link:
                    url = link['href']
                    if not url.startswith('http'):
                        base_url = 'https://www.lifeatcanva.com'
                        url = f"{base_url}{url}" if url.startswith('/') else f"{base_url}/{url}"

            # Try to extract department from the text
            department = "Not specified"
            text_lower = full_text.lower()

            # Common department patterns
            if 'engineering' in text_lower or 'developer' in text_lower or 'software' in text_lower:
                department = "Engineering"
            elif 'design' in text_lower or 'ux' in text_lower or 'ui' in text_lower:
                department = "Design"
            elif 'product' in text_lower and 'manager' in text_lower:
                department = "Product"
            elif 'sales' in text_lower or 'account' in text_lower:
                department = "Sales"
            elif 'marketing' in text_lower or 'growth' in text_lower:
                department = "Marketing"
            elif 'data' in text_lower or 'analytics' in text_lower:
                department = "Data"
            elif 'people' in text_lower or 'hr' in text_lower or 'recruiting' in text_lower:
                department = "People"
            elif 'finance' in text_lower or 'accounting' in text_lower:
                department = "Finance"
            elif 'legal' in text_lower or 'compliance' in text_lower:
                department = "Legal"
            elif 'operations' in text_lower or 'ops' in text_lower:
                department = "Operations"

            # Try to extract location from the full text if not found
            if location == "Not specified":
                # Look for common location patterns
                location_patterns = [
                    r'Location:\s*([^,\n]+)',
                    r'Based in:\s*([^,\n]+)',
                    r'Office:\s*([^,\n]+)',
                    r'City:\s*([^,\n]+)'
                ]

                for pattern in location_patterns:
                    match = re.search(pattern, full_text, re.IGNORECASE)
                    if match:
                        location = match.group(1).strip()
                        break

                # Check for common cities in the text
                cities = ['Sydney', 'Melbourne', 'Austin', 'San Francisco', 'London', 'Remote', 'New York', 'Beijing', 'Manila']
                for city in cities:
                    if city in full_text:
                        location = city
                        break

            # Try to extract salary
            salary = self.extract_salary(full_text)

            return {
                'title': title,
                'url': url,
                'location': location,
                'department': department,
                'salary': salary,
                'salary_min': salary['min'] if salary else None,
                'salary_max': salary['max'] if salary else None,
                'raw_text': full_text[:500],
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing Canva job element: {e}")
            return None

    async def parse_canva_job_link(self, link, page) -> Optional[Dict]:
        """Parse a job from a link element found in Canva's HTML"""
        try:
            title = link.get_text(strip=True)
            url = link.get('href')

            if not url.startswith('http'):
                base_url = 'https://www.lifeatcanva.com'
                url = f"{base_url}{url}" if url.startswith('/') else f"{base_url}/{url}"

            # Extract location if in parentheses in title
            location = "Not specified"
            if '(' in title and ')' in title:
                match = re.search(r'\(([^)]+)\)', title)
                if match:
                    location = match.group(1).strip()
                    title = title.replace(match.group(0), '').strip()

            # Try to infer department from title
            department = "Not specified"
            title_lower = title.lower()

            if 'engineering' in title_lower or 'developer' in title_lower or 'software' in title_lower:
                department = "Engineering"
            elif 'design' in title_lower or 'ux' in title_lower or 'ui' in title_lower:
                department = "Design"
            elif 'product' in title_lower and 'manager' in title_lower:
                department = "Product"
            elif 'sales' in title_lower or 'account' in title_lower:
                department = "Sales"
            elif 'marketing' in title_lower or 'growth' in title_lower:
                department = "Marketing"
            elif 'data' in title_lower or 'analytics' in title_lower:
                department = "Data"

            # Get parent element text for additional context
            parent_text = ""
            parent = link.find_parent(['div', 'article', 'li'])
            if parent:
                parent_text = parent.get_text(strip=True)
                # Try to extract salary from parent text
                salary = self.extract_salary(parent_text)
            else:
                salary = None

            return {
                'title': title,
                'url': url,
                'location': location,
                'department': department,
                'salary': salary,
                'salary_min': salary['min'] if salary else None,
                'salary_max': salary['max'] if salary else None,
                'raw_text': parent_text[:500] if parent_text else title,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing Canva job link: {e}")
            return None

    async def scrape_rippling_jobs(self, company_url: str, fetch_details: bool = True, max_detail_fetches: int = 20) -> List[Dict]:
        """Scrape jobs from Rippling's ATS at rippling.com/careers"""
        page = await self.context.new_page()
        jobs = []

        try:
            logger.info(f"Scraping Rippling site: {company_url}")
            await page.goto(company_url, wait_until='domcontentloaded', timeout=30000)

            # Wait for dynamic content to load
            await page.wait_for_timeout(5000)

            # Scroll to load all jobs
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)

            # Rippling-specific selectors for their ATS
            job_selectors = [
                'a[href*="ats.rippling.com"]',  # Links to ATS
                'a[href*="/rippling/jobs/"]',   # Job links
                '.job-card',
                '.job-listing',
                '.role',
                '.position',
                'div[class*="JobCard"]',
                'div[class*="jobCard"]',
                'article[class*="job"]',
                '[data-testid="job-card"]',
                '[role="listitem"] a',
                'div[class*="opening"]',
                'h3 > a',  # Job titles in headers
                'h4 > a',
                'li a[href*="rippling"]',
                'div[class*="role"] a'
            ]

            job_elements = None
            for selector in job_selectors:
                job_elements = await page.query_selector_all(selector)
                if job_elements and len(job_elements) > 0:
                    # Filter out non-job elements
                    valid_elements = []
                    for elem in job_elements:
                        text = await elem.text_content()
                        if text and len(text.strip()) > 5 and not any(skip in text.lower() for skip in ['cookie', 'privacy', 'terms', 'careers at', 'benefits', 'perks', 'about', 'blog', 'resources']):
                            valid_elements.append(elem)

                    if valid_elements:
                        job_elements = valid_elements
                        logger.info(f"Found {len(job_elements)} jobs using Rippling selector: {selector}")
                        break

            if not job_elements:
                # Try to find job links by pattern in HTML
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                job_links = []
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link['href']
                    text = link.get_text(strip=True)
                    # Check if it's likely a job link (Rippling uses their ATS domain)
                    if text and len(text) > 5 and (
                        'ats.rippling.com' in href or
                        '/rippling/jobs/' in href
                    ) and not any(skip in text.lower() for skip in ['cookie', 'privacy', 'terms', 'careers', 'benefits']):
                        job_links.append(link)

                if job_links:
                    logger.info(f"Found {len(job_links)} job links via href pattern")
                    for link in job_links:
                        job = await self.parse_rippling_job_link(link, page)
                        if job:
                            jobs.append(job)

            # Parse job elements
            detail_fetch_count = 0
            for i, element in enumerate(job_elements):
                try:
                    job = await self.parse_rippling_job_element(element, page)
                    if job:
                        # Try to get salary and more details from job detail page
                        if fetch_details and job.get('url') and detail_fetch_count < max_detail_fetches:
                            try:
                                logger.info(f"Fetching details for Rippling job {i+1}/{len(job_elements)}: {job['title'][:30]}...")
                                details = await self.scrape_rippling_job_details(job['url'])
                                # Update job with details
                                if details.get('salary'):
                                    job['salary'] = details['salary']
                                    job['salary_min'] = details['salary']['min']
                                    job['salary_max'] = details['salary']['max']
                                    logger.info(f"Found salary: ${details['salary']['min']:,} - ${details['salary']['max']:,}")
                                if details.get('location') and job['location'] == "Not specified":
                                    job['location'] = details['location']
                                if details.get('department') and job['department'] == "Not specified":
                                    job['department'] = details['department']
                                detail_fetch_count += 1
                            except Exception as e:
                                logger.debug(f"Could not fetch job details: {e}")
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing Rippling job element: {e}")
                    continue

            logger.info(f"Scraped {len(jobs)} jobs from Rippling site: {company_url}")

        except Exception as e:
            logger.error(f"Error scraping Rippling site {company_url}: {e}")
        finally:
            await page.close()

        return jobs

    async def scrape_rippling_job_details(self, job_url: str) -> Dict:
        """Scrape detailed information from a Rippling ATS job page"""
        page = await self.context.new_page()
        details = {}

        try:
            logger.info(f"Fetching Rippling job details from: {job_url}")
            await page.goto(job_url, wait_until='domcontentloaded', timeout=30000)

            # Wait for content to load
            await page.wait_for_timeout(3000)

            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Extract salary from various possible locations
            salary = None

            # Method 1: Look for compensation/salary sections
            for section in soup.find_all(['div', 'section', 'p', 'li', 'span', 'dd']):
                section_text = section.get_text()
                if '$' in section_text and ('per year' in section_text.lower() or 'annually' in section_text.lower() or '-' in section_text or '–' in section_text):
                    salary = self.extract_salary(section_text)
                    if salary:
                        details['salary'] = salary
                        break

            # Method 2: Look for structured salary data
            if not salary:
                salary_patterns = [
                    r'Salary Range:?\s*\$[\d,]+\s*-\s*\$[\d,]+',
                    r'Compensation:?\s*\$[\d,]+\s*-\s*\$[\d,]+',
                    r'Pay Range:?\s*\$[\d,]+\s*-\s*\$[\d,]+',
                    r'Base Salary:?\s*\$[\d,]+\s*-\s*\$[\d,]+',
                ]

                full_text = soup.get_text()
                for pattern in salary_patterns:
                    match = re.search(pattern, full_text, re.IGNORECASE)
                    if match:
                        salary = self.extract_salary(match.group(0))
                        if salary:
                            details['salary'] = salary
                            break

            # Extract location
            location_elem = soup.find(text=re.compile(r'Location:', re.I))
            if location_elem:
                location = location_elem.parent.get_text().replace('Location:', '').strip()
                details['location'] = location

            # Extract department
            dept_elem = soup.find(text=re.compile(r'Department:|Team:', re.I))
            if dept_elem:
                department = dept_elem.parent.get_text().replace('Department:', '').replace('Team:', '').strip()
                details['department'] = department

        except Exception as e:
            logger.error(f"Error fetching Rippling job details: {e}")
        finally:
            await page.close()

        return details

    async def parse_rippling_job_element(self, element, page) -> Optional[Dict]:
        """Parse a single Rippling job element"""
        try:
            # Get full text and HTML
            full_text = await element.text_content()
            if not full_text:
                return None

            html = await element.inner_html()
            soup = BeautifulSoup(html, 'html.parser')

            # Get job title
            title = None
            title_elem = soup.find(['h3', 'h4', 'h2', 'strong'])
            if title_elem:
                title = title_elem.get_text(strip=True)
            else:
                # Try to find the first link text
                link = soup.find('a')
                if link:
                    title = link.get_text(strip=True)

            if not title:
                # Get first non-empty line
                lines = [line.strip() for line in full_text.strip().split('\n') if line.strip()]
                if lines:
                    title = lines[0]

            if not title:
                return None

            # Get job URL
            url = None
            element_href = await element.get_attribute('href')
            if element_href:
                url = element_href
                if url and not url.startswith('http'):
                    # Construct full URL for Rippling ATS
                    if 'ats.rippling.com' not in url:
                        url = f"https://ats.rippling.com{url}" if url.startswith('/') else f"https://ats.rippling.com/{url}"
            else:
                # Look for a link within the element
                link = soup.find('a', href=True)
                if link:
                    url = link['href']
                    if not url.startswith('http'):
                        if 'ats.rippling.com' not in url:
                            url = f"https://ats.rippling.com{url}" if url.startswith('/') else f"https://ats.rippling.com/{url}"

            # Try to extract location from the text
            location = "Not specified"

            # Look for location patterns
            location_patterns = [
                r'Location:\s*([^,\n]+)',
                r'Based in:\s*([^,\n]+)',
                r'Office:\s*([^,\n]+)',
                r'\(([^)]+)\)',  # Location in parentheses
            ]

            for pattern in location_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    location = match.group(1).strip()
                    break

            # Check for common cities
            if location == "Not specified":
                cities = ['San Francisco', 'New York', 'Austin', 'London', 'Remote', 'Bangalore', 'Dublin', 'Toronto']
                for city in cities:
                    if city in full_text:
                        location = city
                        break

            # Try to extract department from the text
            department = "Not specified"
            text_lower = full_text.lower()

            # Common department patterns
            if 'engineering' in text_lower or 'developer' in text_lower or 'software' in text_lower:
                department = "Engineering"
            elif 'design' in text_lower or 'ux' in text_lower or 'ui' in text_lower:
                department = "Design"
            elif 'product' in text_lower and 'manager' in text_lower:
                department = "Product"
            elif 'sales' in text_lower or 'account' in text_lower:
                department = "Sales"
            elif 'marketing' in text_lower or 'growth' in text_lower:
                department = "Marketing"
            elif 'data' in text_lower or 'analytics' in text_lower:
                department = "Data"
            elif 'people' in text_lower or 'hr' in text_lower or 'recruiting' in text_lower:
                department = "People"
            elif 'finance' in text_lower or 'accounting' in text_lower:
                department = "Finance"
            elif 'legal' in text_lower or 'compliance' in text_lower:
                department = "Legal"
            elif 'operations' in text_lower or 'ops' in text_lower:
                department = "Operations"
            elif 'customer' in text_lower and ('success' in text_lower or 'support' in text_lower):
                department = "Customer Success"

            # Try to extract salary (though it's usually on detail page)
            salary = self.extract_salary(full_text)

            return {
                'title': title,
                'url': url,
                'location': location,
                'department': department,
                'salary': salary,
                'salary_min': salary['min'] if salary else None,
                'salary_max': salary['max'] if salary else None,
                'raw_text': full_text[:500],
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing Rippling job element: {e}")
            return None

    async def parse_rippling_job_link(self, link, page) -> Optional[Dict]:
        """Parse a job from a link element found in Rippling's HTML"""
        try:
            title = link.get_text(strip=True)
            url = link.get('href')

            if not url.startswith('http'):
                if 'ats.rippling.com' not in url:
                    url = f"https://ats.rippling.com{url}" if url.startswith('/') else f"https://ats.rippling.com/{url}"

            # Try to extract location from title or parent
            location = "Not specified"

            # Check for location in parentheses in title
            if '(' in title and ')' in title:
                match = re.search(r'\(([^)]+)\)', title)
                if match:
                    potential_location = match.group(1).strip()
                    # Check if it's likely a location
                    if any(loc_word in potential_location.lower() for loc_word in ['remote', 'office', 'francisco', 'york', 'austin']):
                        location = potential_location
                        title = title.replace(match.group(0), '').strip()

            # Try to infer department from title
            department = "Not specified"
            title_lower = title.lower()

            if 'engineering' in title_lower or 'developer' in title_lower or 'software' in title_lower:
                department = "Engineering"
            elif 'design' in title_lower or 'ux' in title_lower or 'ui' in title_lower:
                department = "Design"
            elif 'product' in title_lower and 'manager' in title_lower:
                department = "Product"
            elif 'sales' in title_lower or 'account' in title_lower:
                department = "Sales"
            elif 'marketing' in title_lower or 'growth' in title_lower:
                department = "Marketing"

            # Get parent element text for additional context
            parent_text = ""
            parent = link.find_parent(['div', 'article', 'li'])
            if parent:
                parent_text = parent.get_text(strip=True)
                # Try to extract salary from parent text (rare but possible)
                salary = self.extract_salary(parent_text)
            else:
                salary = None

            return {
                'title': title,
                'url': url,
                'location': location,
                'department': department,
                'salary': salary,
                'salary_min': salary['min'] if salary else None,
                'salary_max': salary['max'] if salary else None,
                'raw_text': parent_text[:500] if parent_text else title,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing Rippling job link: {e}")
            return None

    async def scrape_stripe_jobs(self, company_url: str, fetch_details: bool = True, max_detail_fetches: int = 20) -> List[Dict]:
        """Scrape jobs from Stripe's custom job board"""
        page = await self.context.new_page()
        jobs = []

        try:
            logger.info(f"Scraping Stripe site: {company_url}")
            await page.goto(company_url, wait_until='networkidle', timeout=30000)

            # Wait for content to load
            await page.wait_for_timeout(3000)

            # Stripe-specific selectors
            job_selectors = [
                'a[href^="/jobs/listing"]',  # Stripe job listing links
                '.JobsListings__item',
                '.JobListing',
                'div[data-testid="job-listing"]',
                'article.job-listing',
                'div[class*="job-card"]',
                'div[class*="JobCard"]',
                'a[class*="JobLink"]',
                '[role="listitem"] a',
                '.jobs-list__item',
                'tbody tr',  # Table rows for job listings
            ]

            job_elements = None
            for selector in job_selectors:
                job_elements = await page.query_selector_all(selector)
                if job_elements and len(job_elements) > 0:
                    logger.info(f"Found {len(job_elements)} jobs using Stripe selector: {selector}")
                    break

            if not job_elements:
                # Try to find job links by pattern
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # Look for links to job listings
                job_links = []
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link['href']
                    text = link.get_text(strip=True)
                    # Stripe job URLs typically contain /jobs/listing/
                    if text and len(text) > 5 and ('/jobs/listing/' in href or 'job' in href.lower()):
                        if not any(skip in text.lower() for skip in ['cookie', 'privacy', 'terms', 'see all', 'view all']):
                            job_links.append(link)

                if job_links:
                    logger.info(f"Found {len(job_links)} job links via pattern matching")
                    for link in job_links:
                        job = await self.parse_stripe_job_link(link, page)
                        if job:
                            jobs.append(job)
                    return jobs

            # Parse job elements
            detail_fetch_count = 0
            for i, element in enumerate(job_elements):
                try:
                    job = await self.parse_stripe_job_element(element, page)
                    if job:
                        # Try to get salary from job detail page if not found
                        if fetch_details and job.get('url') and not job.get('salary') and detail_fetch_count < max_detail_fetches:
                            try:
                                logger.info(f"Fetching salary details for Stripe job {i+1}/{len(job_elements)}: {job['title'][:30]}...")
                                details = await self.scrape_job_details(job['url'])
                                if details.get('salary'):
                                    job['salary'] = details['salary']
                                    logger.info(f"Found salary: ${details['salary']['min']:,} - ${details['salary']['max']:,}")
                                detail_fetch_count += 1
                            except Exception as e:
                                logger.debug(f"Could not fetch job details: {e}")
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing Stripe job element: {e}")
                    continue

            logger.info(f"Scraped {len(jobs)} jobs from Stripe site: {company_url}")

        except Exception as e:
            logger.error(f"Error scraping Stripe site {company_url}: {e}")
        finally:
            await page.close()

        return jobs

    async def parse_stripe_job_element(self, element, page) -> Optional[Dict]:
        """Parse a single Stripe job element (table row)"""
        try:
            # Get full HTML to parse table structure
            html = await element.inner_html()
            soup = BeautifulSoup(html, 'html.parser')

            # Stripe uses table cells: title | department | location
            cells = soup.find_all('td')

            if not cells or len(cells) < 3:
                # Fallback to generic parsing if not a table row
                full_text = await element.text_content()
                if not full_text:
                    return None

                # Try to extract title from link
                title = None
                link = soup.find('a')
                if link:
                    title = link.get_text(strip=True)

                if not title:
                    lines = [line.strip() for line in full_text.strip().split('\n') if line.strip()]
                    if lines:
                        title = lines[0]

                if not title:
                    return None

                department = 'Not specified'
                location = 'Not specified'
            else:
                # Parse table cells
                # Cell 0: Title with link
                title_cell = cells[0]
                title_link = title_cell.find('a')
                title = title_link.get_text(strip=True) if title_link else title_cell.get_text(strip=True)

                # Cell 1: Department
                dept_cell = cells[1]
                department = dept_cell.get_text(strip=True)
                if not department or department == '':
                    department = 'Not specified'

                # Cell 2: Location (with flag icon)
                location_cell = cells[2]
                # Look for span with location name
                location_span = location_cell.find('span', class_='JobsListings__locationDisplayName')
                if location_span:
                    location = location_span.get_text(strip=True)
                else:
                    location = location_cell.get_text(strip=True)

                if not location or location == '':
                    location = 'Not specified'

            # Get job URL
            url = None
            link = soup.find('a', href=True)
            if link:
                url = link['href']
                if url and not url.startswith('http'):
                    # Stripe URLs are relative to stripe.com
                    url = f"https://stripe.com{url}" if url.startswith('/') else f"https://stripe.com/{url}"

            # If department wasn't found in table, infer from title
            if department == 'Not specified' and title:
                title_lower = title.lower()
                if 'engineer' in title_lower or 'developer' in title_lower:
                    department = 'Engineering'
                elif 'product' in title_lower and 'engineer' not in title_lower:
                    department = 'Product'
                elif 'design' in title_lower:
                    department = 'Design'
                elif 'sales' in title_lower or 'account executive' in title_lower:
                    department = 'Sales'
                elif 'marketing' in title_lower or 'growth' in title_lower:
                    department = 'Marketing'
                elif 'data' in title_lower or 'analyst' in title_lower:
                    department = 'Data & Analytics'
                elif 'support' in title_lower or 'success' in title_lower:
                    department = 'Customer Support'
                elif 'legal' in title_lower or 'counsel' in title_lower or 'compliance' in title_lower:
                    department = 'Legal & Compliance'
                elif 'finance' in title_lower or 'accounting' in title_lower:
                    department = 'Finance'
                elif 'operations' in title_lower or ' ops ' in title_lower:
                    department = 'Operations'
                elif 'people' in title_lower or 'hr' in title_lower or 'recruiting' in title_lower:
                    department = 'People & HR'

            # Get salary info from full text
            full_text = await element.text_content() if element else ''
            salary_info = self.extract_salary(full_text)

            return {
                'title': title.strip(),
                'url': url,
                'location': location.strip() if location else 'Not specified',
                'department': department,
                'salary': salary_info,
                'provider': 'stripe',
                'scraped_at': datetime.now().isoformat(),
                'raw_text': full_text
            }

        except Exception as e:
            logger.error(f"Error parsing Stripe job element: {e}")
            return None

    async def parse_stripe_job_link(self, link_soup, page) -> Optional[Dict]:
        """Parse a Stripe job from a link element"""
        try:
            title = link_soup.get_text(strip=True)
            if not title or len(title) < 5:
                return None

            url = link_soup.get('href', '')
            if url and not url.startswith('http'):
                url = f"https://stripe.com{url}" if url.startswith('/') else f"https://stripe.com/{url}"

            # Try to get more context from parent
            parent = link_soup.parent
            full_text = parent.get_text(strip=True) if parent else title

            # Extract location if present
            location = 'Not specified'
            if 'remote' in full_text.lower():
                location = 'Remote'
            else:
                # Look for city names
                for city in ['New York', 'San Francisco', 'Seattle', 'Chicago', 'Dublin', 'London', 'Singapore', 'Tokyo']:
                    if city.lower() in full_text.lower():
                        location = city
                        break

            # Extract department from title
            department = 'Not specified'
            title_lower = title.lower()
            if 'engineer' in title_lower or 'developer' in title_lower:
                department = 'Engineering'
            elif 'product' in title_lower:
                department = 'Product'
            elif 'design' in title_lower:
                department = 'Design'
            elif 'sales' in title_lower:
                department = 'Sales'
            elif 'marketing' in title_lower:
                department = 'Marketing'
            elif 'data' in title_lower:
                department = 'Data & Analytics'

            return {
                'title': title,
                'url': url,
                'location': location,
                'department': department,
                'salary': None,
                'provider': 'stripe',
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing Stripe job link: {e}")
            return None

    async def scrape_databricks_jobs(self, company_url: str, fetch_details: bool = True, max_detail_fetches: int = 20) -> List[Dict]:
        """Scrape jobs from Databricks custom job board"""
        page = await self.context.new_page()
        jobs = []

        try:
            logger.info(f"Scraping Databricks site: {company_url}")
            await page.goto(company_url, wait_until='networkidle', timeout=30000)

            # Wait for content to load
            await page.wait_for_timeout(3000)

            # Databricks-specific selectors - they use links with job ID patterns
            job_selectors = [
                'a[href*="/company/careers/"][href*="-"]',  # Job listing links with IDs
                'a[href*="careers.databricks.com"]',  # External career links
                '.job-listing',
                '.job-card',
                '.position-card',
                'div[class*="JobCard"]',
                'div[class*="job-item"]',
                'article[class*="position"]',
                '[data-testid="job-card"]',
                '.careers-position',
                'li[class*="job"]',
                'div[role="listitem"]',
                'a[class*="position-link"]',
            ]

            job_elements = None
            for selector in job_selectors:
                job_elements = await page.query_selector_all(selector)
                if job_elements and len(job_elements) > 0:
                    # Filter out non-job elements
                    valid_elements = []
                    for elem in job_elements:
                        text = await elem.text_content()
                        if text and len(text.strip()) > 10 and not any(skip in text.lower() for skip in ['cookie', 'privacy', 'terms', 'careers at', 'join us']):
                            valid_elements.append(elem)

                    if valid_elements:
                        job_elements = valid_elements
                        logger.info(f"Found {len(job_elements)} jobs using Databricks selector: {selector}")
                        break

            if not job_elements:
                # Try to find job links by pattern
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # Look for links to job listings
                job_links = []
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link['href']
                    text = link.get_text(strip=True)
                    # Databricks job URLs have specific patterns with job IDs
                    # Example: /company/careers/product/corporate-development--ventures-manager-8160187002
                    if text and len(text) > 15 and len(text) < 150:  # Job titles are typically this length
                        # Check if it's a job link (has careers path with numeric ID at the end)
                        if '/company/careers/' in href and re.search(r'-\d{7,}$', href):
                            if not any(skip in text.lower() for skip in ['cookie', 'privacy', 'terms', 'see all', 'view all', 'learn more', 'careers at', 'join us']):
                                job_links.append(link)
                        # Also check for external careers.databricks.com links
                        elif 'careers.databricks.com' in href:
                            job_links.append(link)

                if job_links:
                    logger.info(f"Found {len(job_links)} job links via pattern matching")
                    for link in job_links:
                        job = await self.parse_databricks_job_link(link, page)
                        if job:
                            jobs.append(job)
                    return jobs

            # Parse job elements
            detail_fetch_count = 0
            for i, element in enumerate(job_elements):
                try:
                    job = await self.parse_databricks_job_element(element, page)
                    if job:
                        # Try to get salary from job detail page if not found
                        if fetch_details and job.get('url') and not job.get('salary') and detail_fetch_count < max_detail_fetches:
                            try:
                                logger.info(f"Fetching salary details for Databricks job {i+1}/{len(job_elements)}: {job['title'][:30]}...")
                                details = await self.scrape_job_details(job['url'])
                                if details.get('salary'):
                                    job['salary'] = details['salary']
                                    logger.info(f"Found salary: ${details['salary']['min']:,} - ${details['salary']['max']:,}")
                                detail_fetch_count += 1
                            except Exception as e:
                                logger.debug(f"Could not fetch job details: {e}")
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing Databricks job element: {e}")
                    continue

            logger.info(f"Scraped {len(jobs)} jobs from Databricks site: {company_url}")

        except Exception as e:
            logger.error(f"Error scraping Databricks site {company_url}: {e}")
        finally:
            await page.close()

        return jobs

    async def parse_databricks_job_element(self, element, page) -> Optional[Dict]:
        """Parse a single Databricks job element"""
        try:
            # For Databricks, the element is usually an anchor tag
            # Get the href attribute directly
            href = await element.get_attribute('href') if element else None

            # Get full text
            full_text = await element.text_content()
            if not full_text:
                return None

            # Databricks embeds location in the title text
            # Format: "Job Title Location, Country" or "Job TitleLocation, Country"
            # Split and clean the title
            lines = [line.strip() for line in full_text.strip().split('\n') if line.strip()]

            # The full text often contains the title and location together
            combined_text = ' '.join(lines)

            # Try to separate title from location
            # Look for common location patterns at the end
            location = None
            title = combined_text

            # Common location patterns
            location_cities = ['San Francisco', 'New York', 'Seattle', 'Amsterdam', 'Berlin', 'Munich',
                             'London', 'Singapore', 'Bengaluru', 'Belgrade', 'Mountain View', 'Toronto',
                             'Paris', 'Tokyo', 'Sydney', 'Tel Aviv', 'Dublin', 'Remote']

            for city in location_cities:
                if city in combined_text:
                    # Extract location and clean title
                    loc_index = combined_text.find(city)
                    if loc_index > 0:
                        title = combined_text[:loc_index].strip()
                        location = combined_text[loc_index:].strip()
                        # Clean up any trailing commas or countries from title
                        title = re.sub(r'[,\s]+$', '', title)
                        break

            # If no location found, check for country names
            if not location:
                countries = ['USA', 'United States', 'India', 'Netherlands', 'Germany', 'UK',
                           'United Kingdom', 'France', 'Japan', 'Canada', 'Australia', 'Israel', 'Serbia']
                for country in countries:
                    if country in combined_text:
                        loc_index = combined_text.rfind(',')  # Find last comma before country
                        if loc_index > 0:
                            title = combined_text[:loc_index].strip()
                            location = combined_text[loc_index+1:].strip()
                            break

            # Build proper URL
            url = None
            if href:
                if href.startswith('http'):
                    url = href
                else:
                    # Databricks uses relative URLs
                    url = f"https://www.databricks.com{href}" if href.startswith('/') else f"https://www.databricks.com/{href}"

            # Parse department from title
            department = 'Not specified'
            title_lower = title.lower()
            if 'engineer' in title_lower or 'developer' in title_lower:
                department = 'Engineering'
            elif 'product' in title_lower and 'engineer' not in title_lower:
                department = 'Product'
            elif 'design' in title_lower:
                department = 'Design'
            elif 'sales' in title_lower or 'account' in title_lower:
                department = 'Sales'
            elif 'marketing' in title_lower or 'growth' in title_lower:
                department = 'Marketing'
            elif 'data scientist' in title_lower or 'analyst' in title_lower:
                department = 'Data & Analytics'
            elif 'support' in title_lower or 'success' in title_lower:
                department = 'Customer Support'
            elif 'legal' in title_lower or 'counsel' in title_lower or 'compliance' in title_lower:
                department = 'Legal & Compliance'
            elif 'finance' in title_lower or 'accounting' in title_lower:
                department = 'Finance'
            elif 'operations' in title_lower or ' ops' in title_lower:
                department = 'Operations'
            elif 'people' in title_lower or 'hr' in title_lower or 'recruiting' in title_lower:
                department = 'People & HR'
            elif 'security' in title_lower:
                department = 'Security'

            # Get salary info
            salary_info = self.extract_salary(full_text)

            return {
                'title': title.strip(),
                'url': url,
                'location': location.strip() if location else 'Not specified',
                'department': department,
                'salary': salary_info,
                'provider': 'databricks',
                'scraped_at': datetime.now().isoformat(),
                'raw_text': full_text
            }

        except Exception as e:
            logger.error(f"Error parsing Databricks job element: {e}")
            return None

    async def parse_databricks_job_link(self, link_soup, page) -> Optional[Dict]:
        """Parse a Databricks job from a link element"""
        try:
            title = link_soup.get_text(strip=True)
            if not title or len(title) < 5:
                return None

            url = link_soup.get('href', '')
            if url and not url.startswith('http'):
                url = f"https://www.databricks.com{url}" if url.startswith('/') else f"https://www.databricks.com/{url}"

            # Try to get more context from parent
            parent = link_soup.parent
            full_text = parent.get_text(strip=True) if parent else title

            # Extract location if present
            location = 'Not specified'
            if 'remote' in full_text.lower():
                location = 'Remote'
            else:
                # Look for city names
                for city in ['New York', 'San Francisco', 'Seattle', 'Amsterdam', 'Berlin', 'Munich', 'London', 'Singapore', 'Bengaluru']:
                    if city.lower() in full_text.lower():
                        location = city
                        break

            # Extract department from title
            department = 'Not specified'
            title_lower = title.lower()
            if 'engineer' in title_lower or 'developer' in title_lower:
                department = 'Engineering'
            elif 'product' in title_lower and 'engineer' not in title_lower:
                department = 'Product'
            elif 'design' in title_lower:
                department = 'Design'
            elif 'sales' in title_lower:
                department = 'Sales'
            elif 'marketing' in title_lower:
                department = 'Marketing'
            elif 'data' in title_lower:
                department = 'Data & Analytics'

            return {
                'title': title,
                'url': url,
                'location': location,
                'department': department,
                'salary': None,
                'provider': 'databricks',
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing Databricks job link: {e}")
            return None

    async def scrape_greenhouse_jobs(self, company_url: str, fetch_details: bool = True, max_detail_fetches: int = 20) -> List[Dict]:
        """Scrape jobs from a Greenhouse-powered careers page"""
        page = await self.context.new_page()
        jobs = []

        try:
            logger.info(f"Scraping {company_url}")
            await page.goto(company_url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(2000)

            # Common Greenhouse selectors - try more specific ones first
            job_selectors = [
                '.opening',  # Most common Greenhouse class
                '[data-mapped="true"]',  # Greenhouse data attribute
                'section.level-0',  # Another common Greenhouse pattern
                '.job-post',
                '.careers-listing',
                'div[class*="opening"]',
                'div[class*="job"]',
                'li[class*="opening"]',
                'li[class*="job"]',
                'tr[class*="job"]',  # Table-based layouts
                '.position',
                '[role="listitem"]',  # Accessibility markup
                'a[href*="/jobs/"]:has(span)',  # Links with nested content
                'a[href*="/careers/"]:has(span)'
            ]

            job_elements = None
            for selector in job_selectors:
                job_elements = await page.query_selector_all(selector)
                if job_elements and len(job_elements) > 0:
                    # Filter out navigation links and empty elements
                    valid_elements = []
                    for elem in job_elements:
                        text = await elem.text_content()
                        if text and len(text.strip()) > 10 and 'cookie' not in text.lower() and 'privacy' not in text.lower():
                            valid_elements.append(elem)

                    if valid_elements:
                        job_elements = valid_elements
                        logger.info(f"Found {len(job_elements)} valid jobs using selector: {selector}")
                        break

            if not job_elements:
                # Try API endpoint
                api_url = f"{company_url}/api/jobs" if '/api/jobs' not in company_url else company_url
                try:
                    response = await page.evaluate(f"""
                        fetch('{api_url}')
                            .then(res => res.json())
                            .catch(err => null)
                    """)
                    if response and 'jobs' in response:
                        for job_data in response['jobs']:
                            jobs.append(self.parse_api_job(job_data))
                        return jobs
                except:
                    pass

            # Parse HTML jobs
            detail_fetch_count = 0
            for i, element in enumerate(job_elements):
                try:
                    job = await self.parse_job_element(element, page)
                    if job:
                        # Try to get salary from job detail page if not found
                        if fetch_details and job.get('url') and not job.get('salary') and detail_fetch_count < max_detail_fetches:
                            try:
                                logger.info(f"Fetching salary details for job {i+1}/{len(job_elements)}: {job['title'][:30]}...")
                                details = await self.scrape_job_details(job['url'])
                                if details.get('salary'):
                                    job['salary'] = details['salary']
                                    logger.info(f"Found salary: ${details['salary']['min']:,} - ${details['salary']['max']:,}")
                                detail_fetch_count += 1
                            except Exception as e:
                                logger.debug(f"Could not fetch job details: {e}")
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing job element: {e}")
                    continue

            logger.info(f"Scraped {len(jobs)} jobs from {company_url}")

        except Exception as e:
            logger.error(f"Error scraping {company_url}: {e}")
        finally:
            await page.close()

        return jobs

    async def parse_job_element(self, element, page) -> Optional[Dict]:
        """Parse a single job element"""
        try:
            # Get full text first for better parsing
            full_text = await element.text_content()
            if not full_text:
                return None

            # Get HTML for better structure parsing
            html = await element.inner_html()
            soup = BeautifulSoup(html, 'html.parser')

            # Get job title
            title = None
            original_title = None
            # Try link text first (most reliable)
            title_link = soup.find('a')
            if title_link:
                original_title = title_link.get_text(strip=True)
                title = original_title
            # Fallback to h3, h4, or first text
            if not title:
                for tag in ['h3', 'h4', 'h2', 'strong']:
                    title_elem = soup.find(tag)
                    if title_elem:
                        original_title = title_elem.get_text(strip=True)
                        title = original_title
                        break
            if not title:
                lines = [line.strip() for line in full_text.strip().split('\n') if line.strip()]
                if lines:
                    original_title = lines[0]
                    title = original_title

            if not title:
                return None

            # Check if location is embedded in title (common pattern: "Title (Location)")
            embedded_location = None
            if '(' in title and ')' in title:
                # Extract location from parentheses - get the last one
                matches = re.findall(r'\(([^)]+)\)', title)
                if matches:
                    potential_location = matches[-1].strip()
                    # Check if it's actually a location (not part of title)
                    location_keywords = ['remote', 'hybrid', 'usa', 'uk', 'india', 'france', 'germany', 'canada',
                                       'australia', 'singapore', 'japan', 'brazil', 'spain', 'italy', 'netherlands',
                                       'united kingdom', 'united states', 'bengaluru', 'são paulo', 'sao paulo']
                    city_keywords = ['new york', 'san francisco', 'london', 'paris', 'tokyo', 'berlin', 'sydney',
                                   'toronto', 'amsterdam', 'madrid', 'rome', 'beijing', 'bangalore', 'mumbai',
                                   'seattle', 'austin', 'boston', 'chicago', 'denver', 'atlanta', 'los angeles',
                                   'bengaluru', 'são paulo', 'sao paulo', 'dublin', 'singapore', 'hong kong']

                    potential_loc_lower = potential_location.lower()
                    # Check if it contains location keywords or city names
                    if (any(keyword in potential_loc_lower for keyword in location_keywords) or
                        any(city in potential_loc_lower for city in city_keywords) or
                        ',' in potential_location):  # Format like "City, Country"
                        embedded_location = potential_location
                        # Remove location from title
                        title = title.replace(f'({potential_location})', '').strip()

            # Get job URL
            url = None
            link = soup.find('a', href=True)
            if link:
                url = link['href']
                if url and not url.startswith('http'):
                    base_url = page.url.split('/jobs')[0].split('/careers')[0]
                    url = f"{base_url}{url}" if url.startswith('/') else f"{base_url}/{url}"

            # Parse location - Greenhouse often uses span tags
            location = None
            # Try finding location by class or content
            for span in soup.find_all(['span', 'div', 'p']):
                text = span.get_text(strip=True)
                if text and len(text) < 100:  # Location strings are usually short
                    lower_text = text.lower()
                    # Check for location indicators
                    if any(loc in lower_text for loc in ['remote', 'hybrid', 'on-site', 'onsite']):
                        location = text
                        break
                    # Check for city names
                    elif any(city in lower_text for city in ['new york', 'san francisco', 'london', 'tokyo', 'paris', 'berlin',
                                                             'seattle', 'austin', 'boston', 'chicago', 'denver', 'atlanta',
                                                             'los angeles', 'washington', 'toronto', 'singapore', 'amsterdam']):
                        location = text
                        break
                    # Check for country/state abbreviations
                    elif re.search(r'\b(USA?|UK|CA|NY|SF|LA|TX|WA|IL|MA|CO|GA|DC)\b', text):
                        location = text
                        break

            # Parse department - often in separate span/div
            department = None
            if not department:
                # Look for department-like text
                for elem in soup.find_all(['span', 'div', 'p']):
                    text = elem.get_text(strip=True)
                    if text and text != title and text != location and len(text) < 50:
                        lower_text = text.lower()
                        # Check for department keywords
                        dept_keywords = ['engineering', 'product', 'design', 'marketing', 'sales', 'business',
                                       'operations', 'finance', 'legal', 'people', 'hr', 'human resources',
                                       'data', 'research', 'support', 'customer', 'security', 'infrastructure',
                                       'analytics', 'growth', 'platform', 'backend', 'frontend', 'fullstack',
                                       'mobile', 'devops', 'sre', 'qa', 'quality']
                        if any(dept in lower_text for dept in dept_keywords):
                            department = text
                            break

            # If still not found, try parsing from structured text
            lines = [line.strip() for line in full_text.strip().split('\n') if line.strip()]

            # Sometimes Greenhouse shows: Title \n Department \n Location
            if len(lines) >= 3 and not location and not department:
                # Second line might be department
                if not department and len(lines) > 1:
                    potential_dept = lines[1]
                    if any(word in potential_dept.lower() for word in ['engineering', 'product', 'design', 'marketing',
                                                                       'sales', 'operations', 'finance', 'data', 'research']):
                        department = potential_dept
                # Third line might be location
                if not location and len(lines) > 2:
                    potential_loc = lines[2] if department else lines[1]
                    if any(word in potential_loc.lower() for word in ['remote', 'hybrid'] +
                           ['new york', 'san francisco', 'london', 'seattle', 'austin']):
                        location = potential_loc

            # Use embedded location if found and no other location detected
            if not location and embedded_location:
                location = embedded_location

            # Final fallbacks
            if not location:
                location = 'Remote' if 'remote' in full_text.lower() else 'Not specified'
            if not department:
                # Try to extract from job title
                title_lower = title.lower()
                if 'engineer' in title_lower or 'developer' in title_lower:
                    department = 'Engineering'
                elif 'product' in title_lower:
                    department = 'Product'
                elif 'design' in title_lower:
                    department = 'Design'
                elif 'sales' in title_lower or 'account' in title_lower:
                    department = 'Sales'
                elif 'marketing' in title_lower or 'growth' in title_lower:
                    department = 'Marketing'
                elif 'data' in title_lower or 'analyst' in title_lower:
                    department = 'Data & Analytics'
                elif 'support' in title_lower or 'success' in title_lower:
                    department = 'Customer Support'
                else:
                    department = 'Not specified'

            # Get salary info
            salary_info = self.extract_salary(full_text)

            return {
                'title': title.strip(),
                'url': url,
                'location': location.strip() if location else 'Not specified',
                'department': department.strip() if department else 'Not specified',
                'salary': salary_info,
                'provider': 'greenhouse',
                'scraped_at': datetime.now().isoformat(),
                'raw_text': full_text
            }

        except Exception as e:
            logger.error(f"Error parsing job element: {e}")
            return None

    def parse_api_job(self, job_data: Dict) -> Dict:
        """Parse job from API response"""
        salary_info = None
        if 'salary' in job_data or 'compensation' in job_data:
            salary_text = job_data.get('salary') or job_data.get('compensation', '')
            salary_info = self.extract_salary(str(salary_text))

        return {
            'title': job_data.get('title', 'Unknown'),
            'url': job_data.get('absolute_url', job_data.get('url')),
            'location': job_data.get('location', {}).get('name') if isinstance(job_data.get('location'), dict) else job_data.get('location', 'Not specified'),
            'department': job_data.get('departments', [{}])[0].get('name') if job_data.get('departments') else 'Not specified',
            'salary': salary_info,
            'scraped_at': datetime.now().isoformat(),
            'job_id': job_data.get('id'),
            'created_at': job_data.get('created_at'),
            'updated_at': job_data.get('updated_at')
        }

    async def scrape_job_details(self, job_url: str) -> Dict:
        """Scrape detailed information from a specific job posting"""
        page = await self.context.new_page()
        details = {}

        try:
            await page.goto(job_url, wait_until='networkidle', timeout=20000)
            await page.wait_for_timeout(1000)

            # Check if this is an Ashby page and wait for dynamic content
            if 'ashbyhq.com' in job_url:
                # Wait for job description content to load
                try:
                    await page.wait_for_selector('[class*="description"], [class*="content"], main', timeout=3000)
                except:
                    pass

            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Extract detailed information
            details['url'] = job_url

            # Get full page text for salary extraction
            full_text = soup.get_text()

            # Look for salary in specific sections first
            salary = None

            # Method 1: Look for compensation/salary sections (enhanced for Ashby)
            for section in soup.find_all(['div', 'section', 'p', 'li', 'span']):
                section_text = section.get_text()
                # Look for salary patterns even without keywords (common in Notion)
                if '$' in section_text and ('per year' in section_text.lower() or 'annually' in section_text.lower() or '-' in section_text or '–' in section_text):
                    salary = self.extract_salary(section_text)
                    if salary:
                        logger.info(f"Found salary in section: {section_text[:100]}...")
                        break
                # Also check for compensation keywords
                if any(keyword in section_text.lower() for keyword in ['compensation', 'salary', 'pay range', 'wage', 'remuneration', 'total comp', 'base salary']):
                    salary = self.extract_salary(section_text)
                    if salary:
                        logger.info(f"Found salary near keyword: {section_text[:100]}...")
                        break

            # Method 2: Look near specific headers
            if not salary:
                for header in soup.find_all(['h2', 'h3', 'h4', 'h5', 'strong', 'b']):
                    header_text = header.get_text().lower()
                    if any(keyword in header_text for keyword in ['compensation', 'salary', 'pay', 'what you\'ll earn', 'total comp']):
                        # Get the next sibling or parent's text
                        next_elem = header.find_next_sibling()
                        if next_elem:
                            salary = self.extract_salary(next_elem.get_text())
                        if not salary:
                            # Try the next few siblings
                            for i in range(3):
                                next_elem = next_elem.find_next_sibling() if next_elem else None
                                if next_elem:
                                    salary = self.extract_salary(next_elem.get_text())
                                    if salary:
                                        break
                        if not salary and header.parent:
                            salary = self.extract_salary(header.parent.get_text())
                        if salary:
                            logger.info(f"Found salary near header '{header.get_text()}'")
                            break

            # Method 3: Look in job details section (often in dl/dt/dd format)
            if not salary:
                for dl in soup.find_all('dl'):
                    dl_text = dl.get_text()
                    if '$' in dl_text or any(word in dl_text.lower() for word in ['salary', 'compensation', 'pay']):
                        salary = self.extract_salary(dl_text)
                        if salary:
                            logger.info(f"Found salary in dl element")
                            break

            # Method 4: Look for salary in bullet points or list items (common in Ashby/Notion)
            if not salary:
                for li in soup.find_all('li'):
                    li_text = li.get_text()
                    if '$' in li_text and len(li_text) < 200:  # Salary info is usually concise
                        salary = self.extract_salary(li_text)
                        if salary:
                            logger.info(f"Found salary in list item: {li_text[:100]}...")
                            break

            # Method 5: Try searching in specific Ashby class patterns
            if not salary and 'ashbyhq.com' in job_url:
                # Ashby often uses specific classes for job details
                for class_pattern in ['job-posting', 'posting-content', 'job-description', 'rich-text']:
                    elements = soup.find_all(class_=re.compile(class_pattern, re.I))
                    for elem in elements:
                        elem_text = elem.get_text()
                        if '$' in elem_text:
                            salary = self.extract_salary(elem_text)
                            if salary:
                                logger.info(f"Found salary in Ashby element with class '{class_pattern}'")
                                break
                    if salary:
                        break

            # Method 6: Try full page text as last resort
            if not salary:
                salary = self.extract_salary(full_text)
                if salary:
                    logger.info(f"Found salary in full page text")

            details['salary'] = salary

            # Get job description (limit to first 2000 chars for performance)
            desc_element = soup.find(class_=re.compile('description|content|body|posting-description|rich-text'))
            if desc_element:
                details['description'] = desc_element.get_text(strip=True)[:2000]
            else:
                # Try to find main content area
                main_content = soup.find(['main', 'article']) or soup.find(id=re.compile('content|main|job'))
                if main_content:
                    details['description'] = main_content.get_text(strip=True)[:2000]

        except Exception as e:
            logger.debug(f"Error scraping job details from {job_url}: {e}")
        finally:
            await page.close()

        return details


async def scrape_company(company_url: str) -> List[Dict]:
    """Main function to scrape a company's jobs from any supported provider"""
    scraper = TalentScraper()
    await scraper.initialize()

    try:
        jobs = await scraper.scrape_jobs(company_url)
        return jobs
    finally:
        await scraper.close()


if __name__ == "__main__":
    # Test with a known Greenhouse company
    test_url = "https://job-boards.greenhouse.io/anthropic"

    async def test():
        jobs = await scrape_company(test_url)
        print(f"Found {len(jobs)} jobs")
        if jobs:
            print(json.dumps(jobs[0], indent=2))

    asyncio.run(test())