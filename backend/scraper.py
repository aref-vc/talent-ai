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
    """Universal scraper for Greenhouse job boards"""

    def __init__(self):
        self.browser = None
        self.context = None

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

        # Pattern 2: $XXX,XXX - $XXX,XXX
        match = re.search(r'\$(\d{1,3}(?:,\d{3})*)\s*[-–—]\s*\$(\d{1,3}(?:,\d{3})*)', text)
        if match:
            min_sal = match.group(1).replace(',', '')
            max_sal = match.group(2).replace(',', '')
            return {
                'min': int(min_sal),
                'max': int(max_sal),
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

        # Pattern 4: XXX,XXX - XXX,XXX USD/per year
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

            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Extract detailed information
            details['url'] = job_url

            # Get full page text for salary extraction
            full_text = soup.get_text()

            # Look for salary in specific sections first
            salary = None

            # Method 1: Look for compensation/salary sections
            for section in soup.find_all(['div', 'section', 'p', 'li']):
                section_text = section.get_text()
                if any(keyword in section_text.lower() for keyword in ['compensation', 'salary', 'pay range', 'wage', 'remuneration']):
                    salary = self.extract_salary(section_text)
                    if salary:
                        break

            # Method 2: Look near specific headers
            if not salary:
                for header in soup.find_all(['h2', 'h3', 'h4', 'strong']):
                    if any(keyword in header.get_text().lower() for keyword in ['compensation', 'salary', 'pay']):
                        # Get the next sibling or parent's text
                        next_elem = header.find_next_sibling()
                        if next_elem:
                            salary = self.extract_salary(next_elem.get_text())
                        if not salary and header.parent:
                            salary = self.extract_salary(header.parent.get_text())
                        if salary:
                            break

            # Method 3: Look in job details section (often in dl/dt/dd format)
            if not salary:
                for dl in soup.find_all('dl'):
                    dl_text = dl.get_text()
                    if '$' in dl_text or any(word in dl_text.lower() for word in ['salary', 'compensation', 'pay']):
                        salary = self.extract_salary(dl_text)
                        if salary:
                            break

            # Method 4: Try full page text as last resort
            if not salary:
                salary = self.extract_salary(full_text)

            details['salary'] = salary

            # Get job description (limit to first 2000 chars for performance)
            desc_element = soup.find(class_=re.compile('description|content|body|posting-description'))
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
    """Main function to scrape a company's jobs"""
    scraper = TalentScraper()
    await scraper.initialize()

    try:
        jobs = await scraper.scrape_greenhouse_jobs(company_url)
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