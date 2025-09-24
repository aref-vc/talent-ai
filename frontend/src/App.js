import React, { useState, useEffect } from 'react';
import './App.css';
import LandingPage from './components/LandingPage';
import SearchPanel from './components/SearchPanel';
import JobsTable from './components/JobsTable';
import Analytics from './components/Analytics';
import axios from 'axios';

const API_URL = 'http://localhost:8100';

function App() {
  const [jobs, setJobs] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [companyName, setCompanyName] = useState('');
  const [activeTab, setActiveTab] = useState('landing');
  const [recentCompanies, setRecentCompanies] = useState([]);

  useEffect(() => {
    // Load recent companies on mount
    loadRecentCompanies();
  }, []);

  const loadRecentCompanies = async () => {
    try {
      const response = await axios.get(`${API_URL}/companies`);
      setRecentCompanies(response.data.companies || []);
    } catch (err) {
      console.error('Error loading recent companies:', err);
    }
  };

  const handleScrape = async (url, name) => {
    setLoading(true);
    setError(null);
    setJobs([]);
    setAnalytics(null);

    try {
      const response = await axios.post(`${API_URL}/scrape`, {
        company_url: url,
        company_name: name
      });

      if (response.data.success) {
        setJobs(response.data.jobs);
        setAnalytics(response.data.metadata.analytics);
        setCompanyName(response.data.company_name);
        setActiveTab('results');
        loadRecentCompanies(); // Refresh recent companies
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to scrape jobs. Please check the URL and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadCompany = async (companyName) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`${API_URL}/analytics/${companyName}`);
      setAnalytics(response.data);
      setCompanyName(companyName);
      setActiveTab('analytics');
    } catch (err) {
      setError('Failed to load company data');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    try {
      const response = await axios.get(`${API_URL}/export/${companyName}?format=${format}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${companyName}_export.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Failed to export data');
    }
  };

  const handleStartAnalyzing = () => {
    setActiveTab('search');
  };

  return (
    <div className="App">
      {activeTab !== 'landing' && (
        <>
          <header className="App-header">
            <div className="header-content">
              <button
                className="home-btn"
                onClick={() => setActiveTab('landing')}
                title="Back to Home"
              >
                ←
              </button>
              <div className="header-text">
                <h1>🎯 Talent AI</h1>
                <p>Universal Job Scraping & Talent Intelligence Platform</p>
              </div>
            </div>
          </header>

          <nav className="tabs">
            <button
              className={activeTab === 'search' ? 'tab active' : 'tab'}
              onClick={() => setActiveTab('search')}
            >
              Search
            </button>
            <button
              className={activeTab === 'results' ? 'tab active' : 'tab'}
              onClick={() => setActiveTab('results')}
              disabled={jobs.length === 0}
            >
              Results ({jobs.length})
            </button>
            <button
              className={activeTab === 'analytics' ? 'tab active' : 'tab'}
              onClick={() => setActiveTab('analytics')}
              disabled={!analytics}
            >
              Analytics
            </button>
          </nav>
        </>
      )}

      <main className="App-main">
        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Scraping job data... This may take a minute...</p>
          </div>
        )}

        {activeTab === 'landing' && (
          <LandingPage onStartAnalyzing={handleStartAnalyzing} />
        )}

        {activeTab === 'search' && (
          <SearchPanel
            onScrape={handleScrape}
            recentCompanies={recentCompanies}
            onLoadCompany={handleLoadCompany}
          />
        )}

        {activeTab === 'results' && jobs.length > 0 && (
          <div className="results-container">
            <div className="results-header">
              <h2>{companyName}</h2>
              <div className="export-buttons">
                <button onClick={() => handleExport('json')} className="export-btn">
                  Export JSON
                </button>
                <button onClick={() => handleExport('csv')} className="export-btn">
                  Export CSV
                </button>
              </div>
            </div>
            <JobsTable jobs={jobs} />
          </div>
        )}

        {activeTab === 'analytics' && analytics && (
          <div className="analytics-container">
            <h2>{companyName} - Talent Analytics</h2>
            <Analytics data={analytics} companyName={companyName} />
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>© 2024 Talent AI | Powered by Playwright & FastAPI</p>
      </footer>
    </div>
  );
}

export default App;