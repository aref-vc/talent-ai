#!/usr/bin/env python3
"""Test analytics with sample data"""

import json
from datetime import datetime
from app import calculate_analytics

# Sample jobs data with various attributes
sample_jobs = [
    {
        "title": "Senior Software Engineer",
        "url": "https://example.com/job1",
        "location": "San Francisco, CA",
        "department": "Engineering",
        "salary": {"min": 180000, "max": 250000}
    },
    {
        "title": "Product Manager",
        "url": "https://example.com/job2",
        "location": "New York, NY (Remote)",
        "department": "Product",
        "salary": {"min": 150000, "max": 200000}
    },
    {
        "title": "Data Scientist",
        "url": "https://example.com/job3",
        "location": "Remote",
        "department": "Data",
        "salary": {"min": 140000, "max": 190000}
    },
    {
        "title": "Junior Developer",
        "url": "https://example.com/job4",
        "location": "Austin, TX (Hybrid)",
        "department": "Engineering",
        "salary": {"min": 80000, "max": 110000}
    },
    {
        "title": "Senior Product Designer",
        "url": "https://example.com/job5",
        "location": "Seattle, WA",
        "department": "Design",
        "salary": {"min": 160000, "max": 210000}
    },
    {
        "title": "Engineering Manager",
        "url": "https://example.com/job6",
        "location": "Boston, MA",
        "department": "Engineering",
        "salary": {"min": 200000, "max": 280000}
    },
    {
        "title": "Marketing Lead",
        "url": "https://example.com/job7",
        "location": "Los Angeles, CA",
        "department": "Marketing",
        "salary": None
    },
    {
        "title": "Principal Engineer",
        "url": "https://example.com/job8",
        "location": "Remote",
        "department": "Engineering",
        "salary": {"min": 220000, "max": 320000}
    },
    {
        "title": "Associate Product Manager",
        "url": "https://example.com/job9",
        "location": "Chicago, IL",
        "department": "Product",
        "salary": {"min": 90000, "max": 120000}
    },
    {
        "title": "Staff Software Engineer",
        "url": "https://example.com/job10",
        "location": "Denver, CO (Hybrid)",
        "department": "Engineering",
        "salary": {"min": 200000, "max": 270000}
    }
]

# Calculate analytics
analytics = calculate_analytics(sample_jobs)

# Save to file for the API to use
import os
os.makedirs("data", exist_ok=True)
test_data = {
    'url': 'https://example.com/jobs',
    'jobs': sample_jobs,
    'analytics': analytics,
    'scraped_at': datetime.now().isoformat()
}

# Save to file
with open('data/test_company_20240924_000000.json', 'w') as f:
    json.dump(test_data, f, indent=2)

# Print analytics results
print("Analytics Results:")
print(f"Total Jobs: {analytics['total_jobs']}")
print(f"\nSalary Distribution: {analytics.get('salary_distribution', {})}")
print(f"\nWork Arrangement: {analytics.get('work_arrangement', {})}")
print(f"\nSeniority Levels: {analytics.get('seniority_levels', {})}")
print(f"\nAverage Salary by Department:")
for dept, data in analytics.get('avg_salary_by_dept', {}).items():
    if data.get('avg'):
        print(f"  {dept}: ${data['avg']:,}")
print(f"\nTop Paying Jobs: {len(analytics.get('top_paying_jobs', []))} jobs")