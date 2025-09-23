import React, { useState } from 'react';
import './SearchPanel.css';

const EXAMPLE_COMPANIES = [
  { name: 'OpenAI', url: 'https://jobs.ashbyhq.com/openai' },
  { name: 'Anthropic', url: 'https://job-boards.greenhouse.io/anthropic' },
  { name: 'Stripe', url: 'https://stripe.com/jobs/search' },
  { name: 'Coinbase', url: 'https://job-boards.greenhouse.io/coinbase' },
  { name: 'Discord', url: 'https://job-boards.greenhouse.io/discord' },
  { name: 'Figma', url: 'https://job-boards.greenhouse.io/figma' },
  { name: 'Databricks', url: 'https://job-boards.greenhouse.io/databricks' },
  { name: 'Notion', url: 'https://job-boards.greenhouse.io/notion' },
  { name: 'Canva', url: 'https://job-boards.greenhouse.io/canva' },
  { name: 'Scale AI', url: 'https://job-boards.greenhouse.io/scaleai' },
  { name: 'Ramp', url: 'https://job-boards.greenhouse.io/ramp' },
  { name: 'Rippling', url: 'https://job-boards.greenhouse.io/rippling' },
];

function SearchPanel({ onScrape, recentCompanies, onLoadCompany }) {
  const [url, setUrl] = useState('');
  const [companyName, setCompanyName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url) {
      onScrape(url, companyName);
    }
  };

  const handleExampleClick = (example) => {
    setUrl(example.url);
    setCompanyName(example.name);
  };

  return (
    <div className="search-panel">
      <div className="search-card">
        <h2>🔍 Scrape Job Listings</h2>
        <p className="subtitle">Enter a Greenhouse job board URL to analyze talent data</p>

        <form onSubmit={handleSubmit} className="search-form">
          <div className="input-group">
            <label>Company URL *</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://job-boards.greenhouse.io/company"
              required
            />
          </div>

          <div className="input-group">
            <label>Company Name (optional)</label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="e.g., OpenAI"
            />
          </div>

          <button type="submit" className="submit-btn">
            Start Scraping
          </button>
        </form>

        <div className="examples">
          <h3>Quick Start - Example Companies:</h3>
          <div className="example-grid">
            {EXAMPLE_COMPANIES.map((example) => (
              <button
                key={example.name}
                className="example-btn"
                onClick={() => handleExampleClick(example)}
              >
                {example.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {recentCompanies.length > 0 && (
        <div className="recent-card">
          <h3>📊 Recently Scraped</h3>
          <div className="recent-list">
            {recentCompanies.map((company) => (
              <div key={company.name} className="recent-item">
                <div className="recent-info">
                  <span className="company-name">{company.name}</span>
                  <span className="job-count">{company.total_jobs} jobs</span>
                </div>
                <button
                  className="load-btn"
                  onClick={() => onLoadCompany(company.name)}
                >
                  Load Analytics
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchPanel;