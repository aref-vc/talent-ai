#!/usr/bin/env python3
"""
Talent AI - FastAPI Backend
Universal job scraper and talent intelligence platform
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional
import json
import os
from datetime import datetime
import asyncio
from scraper import scrape_company, TalentScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Talent AI",
    description="Universal talent intelligence and job scraping platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3100"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScrapeRequest(BaseModel):
    """Request model for scraping jobs"""
    company_url: HttpUrl = Field(..., description="Greenhouse job board URL")
    company_name: Optional[str] = Field(None, description="Company name for reference")


class JobData(BaseModel):
    """Job data model"""
    title: str
    url: Optional[str]
    location: str
    department: str
    salary: Optional[Dict]
    scraped_at: str
    raw_text: Optional[str]


class ScrapeResponse(BaseModel):
    """Response model for scrape results"""
    success: bool
    company_name: str
    total_jobs: int
    jobs: List[Dict]
    metadata: Dict


class CompanyAnalytics(BaseModel):
    """Analytics response model"""
    total_jobs: int
    departments: Dict[str, int]
    locations: Dict[str, int]
    salary_ranges: Dict
    disclosure_rate: float
    avg_salary: Optional[Dict]
    # New analytics fields
    salary_distribution: Optional[Dict[str, int]] = {}
    avg_salary_by_dept: Optional[Dict[str, Dict]] = {}
    work_arrangement: Optional[Dict[str, int]] = {}
    top_paying_jobs: Optional[List[Dict]] = []
    seniority_levels: Optional[Dict[str, int]] = {}


# In-memory storage for demo (use database in production)
scraped_data = {}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Talent AI",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "/scrape": "POST - Scrape company jobs",
            "/companies": "GET - List scraped companies",
            "/analytics/{company_name}": "GET - Get company analytics",
            "/export/{company_name}": "GET - Export company data",
            "/docs": "API documentation"
        }
    }


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_jobs(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Scrape jobs from a company's Greenhouse board
    """
    try:
        # Extract company name from URL if not provided
        company_name = request.company_name
        if not company_name:
            url_parts = str(request.company_url).split('/')
            for part in url_parts:
                if part and part not in ['https:', 'http:', 'www', 'job-boards.greenhouse.io']:
                    company_name = part
                    break

        if not company_name:
            company_name = "unknown"

        logger.info(f"Starting scrape for {company_name} from {request.company_url}")

        # Scrape jobs
        jobs = await scrape_company(str(request.company_url))

        # Calculate analytics
        analytics = calculate_analytics(jobs)

        # Store data
        scraped_data[company_name] = {
            'url': str(request.company_url),
            'jobs': jobs,
            'analytics': analytics,
            'scraped_at': datetime.now().isoformat()
        }

        # Save to file
        save_path = f"data/{company_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("data", exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(scraped_data[company_name], f, indent=2)

        return ScrapeResponse(
            success=True,
            company_name=company_name,
            total_jobs=len(jobs),
            jobs=jobs,
            metadata={
                'scraped_at': datetime.now().isoformat(),
                'url': str(request.company_url),
                'analytics': analytics
            }
        )

    except Exception as e:
        logger.error(f"Error scraping {request.company_url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/companies")
async def list_companies():
    """List all scraped companies"""
    companies = []
    for name, data in scraped_data.items():
        companies.append({
            'name': name,
            'url': data['url'],
            'total_jobs': len(data['jobs']),
            'scraped_at': data['scraped_at']
        })
    return {'companies': companies}


@app.get("/analytics/{company_name}", response_model=CompanyAnalytics)
async def get_analytics(company_name: str):
    """Get analytics for a specific company"""
    if company_name not in scraped_data:
        # Try loading from file
        files = os.listdir('data') if os.path.exists('data') else []
        for file in files:
            if file.startswith(company_name) and file.endswith('.json'):
                with open(f'data/{file}', 'r') as f:
                    scraped_data[company_name] = json.load(f)
                break

    if company_name not in scraped_data:
        raise HTTPException(status_code=404, detail=f"Company {company_name} not found")

    analytics = scraped_data[company_name].get('analytics')
    if not analytics:
        analytics = calculate_analytics(scraped_data[company_name]['jobs'])

    return CompanyAnalytics(**analytics)


@app.get("/export/{company_name}")
async def export_data(company_name: str, format: str = "json"):
    """Export company data in various formats"""
    if company_name not in scraped_data:
        raise HTTPException(status_code=404, detail=f"Company {company_name} not found")

    data = scraped_data[company_name]

    if format == "json":
        filename = f"{company_name}_export.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return FileResponse(filename, media_type="application/json", filename=filename)

    elif format == "csv":
        import pandas as pd
        df = pd.DataFrame(data['jobs'])
        filename = f"{company_name}_export.csv"
        df.to_csv(filename, index=False)
        return FileResponse(filename, media_type="text/csv", filename=filename)

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


@app.post("/scrape-details")
async def scrape_job_details(job_url: str):
    """Scrape detailed information from a specific job posting"""
    try:
        scraper = TalentScraper()
        await scraper.initialize()
        details = await scraper.scrape_job_details(job_url)
        await scraper.close()
        return details
    except Exception as e:
        logger.error(f"Error scraping job details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def calculate_analytics(jobs: List[Dict]) -> Dict:
    """Calculate analytics from job data"""
    analytics = {
        'total_jobs': len(jobs),
        'departments': {},
        'locations': {},
        'salary_ranges': {
            'with_salary': 0,
            'without_salary': 0,
            'ranges': []
        },
        'disclosure_rate': 0.0,
        'avg_salary': None,
        # New analytics
        'salary_distribution': {},
        'avg_salary_by_dept': {},
        'work_arrangement': {'Remote': 0, 'Hybrid': 0, 'Onsite': 0},
        'top_paying_jobs': [],
        'seniority_levels': {'Entry': 0, 'Mid': 0, 'Senior': 0, 'Lead': 0, 'Principal/Staff': 0}
    }

    # Collect all jobs with salaries for top paying analysis
    jobs_with_salaries = []

    # Count departments and locations
    for job in jobs:
        dept = job.get('department', 'Unknown')
        analytics['departments'][dept] = analytics['departments'].get(dept, 0) + 1

        loc = job.get('location', 'Unknown')
        analytics['locations'][loc] = analytics['locations'].get(loc, 0) + 1

        # Work arrangement analysis (Remote/Hybrid/Onsite)
        loc_lower = loc.lower()
        if 'remote' in loc_lower:
            analytics['work_arrangement']['Remote'] += 1
        elif 'hybrid' in loc_lower:
            analytics['work_arrangement']['Hybrid'] += 1
        else:
            analytics['work_arrangement']['Onsite'] += 1

        # Seniority level analysis
        title = job.get('title', '').lower()
        if any(word in title for word in ['junior', 'entry', 'associate', 'intern', 'graduate']):
            analytics['seniority_levels']['Entry'] += 1
        elif any(word in title for word in ['senior', 'sr.', 'sr ']):
            analytics['seniority_levels']['Senior'] += 1
        elif any(word in title for word in ['lead', 'manager', 'head', 'director']):
            analytics['seniority_levels']['Lead'] += 1
        elif any(word in title for word in ['principal', 'staff', 'architect', 'expert']):
            analytics['seniority_levels']['Principal/Staff'] += 1
        else:
            analytics['seniority_levels']['Mid'] += 1

        # Salary analysis
        if job.get('salary'):
            analytics['salary_ranges']['with_salary'] += 1
            analytics['salary_ranges']['ranges'].append(job['salary'])

            # Collect for top paying jobs
            if job.get('salary', {}).get('max'):
                jobs_with_salaries.append(job)

            # Calculate average for department
            if dept not in analytics['avg_salary_by_dept']:
                analytics['avg_salary_by_dept'][dept] = {'total': 0, 'count': 0, 'avg': 0}

            salary_min = job['salary'].get('min', 0)
            salary_max = job['salary'].get('max', 0)
            avg = (salary_min + salary_max) / 2 if (salary_min and salary_max) else salary_max or salary_min

            if avg:
                analytics['avg_salary_by_dept'][dept]['total'] += avg
                analytics['avg_salary_by_dept'][dept]['count'] += 1

            # Salary distribution (bands)
            max_salary = job['salary'].get('max', 0)
            if max_salary:
                if max_salary < 50000:
                    band = '$0-50k'
                elif max_salary < 100000:
                    band = '$50k-100k'
                elif max_salary < 150000:
                    band = '$100k-150k'
                elif max_salary < 200000:
                    band = '$150k-200k'
                elif max_salary < 250000:
                    band = '$200k-250k'
                else:
                    band = '$250k+'

                analytics['salary_distribution'][band] = analytics['salary_distribution'].get(band, 0) + 1
        else:
            analytics['salary_ranges']['without_salary'] += 1

    # Calculate average salaries per department
    for dept in analytics['avg_salary_by_dept']:
        if analytics['avg_salary_by_dept'][dept]['count'] > 0:
            analytics['avg_salary_by_dept'][dept]['avg'] = int(
                analytics['avg_salary_by_dept'][dept]['total'] /
                analytics['avg_salary_by_dept'][dept]['count']
            )

    # Get top 10 highest paying jobs
    jobs_with_salaries.sort(key=lambda x: x.get('salary', {}).get('max', 0), reverse=True)
    analytics['top_paying_jobs'] = [
        {
            'title': job.get('title', 'Unknown'),
            'department': job.get('department', 'Unknown'),
            'location': job.get('location', 'Unknown'),
            'salary_min': job.get('salary', {}).get('min'),
            'salary_max': job.get('salary', {}).get('max'),
            'url': job.get('url', '')
        }
        for job in jobs_with_salaries[:10]
    ]

    # Ensure salary distribution bands are ordered
    band_order = ['$0-50k', '$50k-100k', '$100k-150k', '$150k-200k', '$200k-250k', '$250k+']
    ordered_distribution = {}
    for band in band_order:
        if band in analytics['salary_distribution']:
            ordered_distribution[band] = analytics['salary_distribution'][band]
    analytics['salary_distribution'] = ordered_distribution

    # Calculate disclosure rate
    if jobs:
        analytics['disclosure_rate'] = (analytics['salary_ranges']['with_salary'] / len(jobs)) * 100

    # Calculate average salary
    if analytics['salary_ranges']['ranges']:
        min_salaries = [s['min'] for s in analytics['salary_ranges']['ranges'] if s.get('min')]
        max_salaries = [s['max'] for s in analytics['salary_ranges']['ranges'] if s.get('max')]

        if min_salaries and max_salaries:
            analytics['avg_salary'] = {
                'min': sum(min_salaries) // len(min_salaries),
                'max': sum(max_salaries) // len(max_salaries)
            }

    return analytics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100, reload=True)