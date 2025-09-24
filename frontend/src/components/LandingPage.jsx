import React, { useState } from 'react';
import './LandingPage.css';

const LandingPage = ({ onStartAnalyzing }) => {
  const [hoveredFeature, setHoveredFeature] = useState(null);

  const features = [
    {
      id: 1,
      icon: 'analytics',
      title: 'Universal Analytics',
      description: '7 comprehensive charts analyzing salary, location, and department distribution across any company',
      metric: '100+ companies supported'
    },
    {
      id: 2,
      icon: 'attach_money',
      title: 'Salary Intelligence',
      description: 'Real-time salary transparency with range detection and competitive benchmarking',
      metric: '$50K-$500K+ range detection'
    },
    {
      id: 3,
      icon: 'location_on',
      title: 'Location Insights',
      description: 'Geographic distribution analysis with remote work classification and trend tracking',
      metric: '50+ locations tracked'
    },
    {
      id: 4,
      icon: 'business',
      title: 'Department Analysis',
      description: 'Smart department classification with growth trend analysis and hiring patterns',
      metric: '15+ departments classified'
    },
    {
      id: 5,
      icon: 'speed',
      title: 'Real-time Data',
      description: 'Live job scraping from multiple career platforms with instant analytics',
      metric: '<2min processing time'
    },
    {
      id: 6,
      icon: 'trending_up',
      title: 'Competitive Analysis',
      description: 'Compare talent strategies across companies with market positioning insights',
      metric: 'Multi-company benchmarking'
    }
  ];

  const topCompanies = [
    {
      name: 'OpenAI',
      logo: 'https://logo.clearbit.com/openai.com',
      jobs: '45+ roles'
    },
    {
      name: 'Anthropic',
      logo: 'https://logo.clearbit.com/anthropic.com',
      jobs: '32+ roles'
    },
    {
      name: 'Stripe',
      logo: 'https://logo.clearbit.com/stripe.com',
      jobs: '67+ roles'
    },
    {
      name: 'Notion',
      logo: 'https://logo.clearbit.com/notion.so',
      jobs: '28+ roles'
    },
    {
      name: 'Canva',
      logo: 'https://logo.clearbit.com/canva.com',
      jobs: '89+ roles'
    },
    {
      name: 'Ramp',
      logo: 'https://logo.clearbit.com/ramp.com',
      jobs: '41+ roles'
    }
  ];

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="badge-text">Universal Talent Intelligence</span>
          </div>
          <h1 className="hero-title">
            Transform Job Data Into
            <span className="highlight"> Strategic Intelligence</span>
          </h1>
          <p className="hero-description">
            Scrape, analyze, and benchmark talent data from any company's career platform.
            Get salary insights, location distribution, and competitive intelligence in minutes.
          </p>
          <div className="hero-stats">
            <div className="stat">
              <span className="stat-number">100+</span>
              <span className="stat-label">Companies Supported</span>
            </div>
            <div className="stat">
              <span className="stat-number">7</span>
              <span className="stat-label">Analytics Charts</span>
            </div>
            <div className="stat">
              <span className="stat-number">&lt;2min</span>
              <span className="stat-label">Processing Time</span>
            </div>
          </div>
          <div className="hero-actions">
            <button className="cta-primary" onClick={onStartAnalyzing}>
              <span className="material-icons cta-icon">rocket_launch</span>
              Start Analyzing
            </button>
          </div>
        </div>
        <div className="hero-visual">
          <div className="analytics-preview">
            <div className="preview-card">
              <div className="card-header">
                <div className="card-title">Salary Distribution</div>
                <div className="card-metric">67% disclosed</div>
              </div>
              <div className="chart-placeholder">
                <div className="chart-bar" style={{ width: '85%', backgroundColor: 'var(--primary)' }}></div>
                <div className="chart-bar" style={{ width: '72%', backgroundColor: 'var(--accent)' }}></div>
                <div className="chart-bar" style={{ width: '58%', backgroundColor: 'var(--secondary)' }}></div>
              </div>
            </div>
            <div className="preview-card">
              <div className="card-header">
                <div className="card-title">Department Split</div>
                <div className="card-metric">12 departments</div>
              </div>
              <div className="doughnut-placeholder">
                <div className="doughnut-segment" style={{ '--start': '0deg', '--end': '120deg', backgroundColor: 'var(--primary)' }}></div>
                <div className="doughnut-segment" style={{ '--start': '120deg', '--end': '200deg', backgroundColor: 'var(--accent)' }}></div>
                <div className="doughnut-segment" style={{ '--start': '200deg', '--end': '280deg', backgroundColor: 'var(--secondary)' }}></div>
                <div className="doughnut-segment" style={{ '--start': '280deg', '--end': '360deg', backgroundColor: 'var(--border)' }}></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="section-header">
          <h2 className="section-title">Comprehensive Talent Intelligence</h2>
          <p className="section-description">
            Everything you need to understand talent markets and competitive positioning
          </p>
        </div>
        <div className="features-grid">
          {features.map((feature) => (
            <div
              key={feature.id}
              className={`feature-card ${hoveredFeature === feature.id ? 'hovered' : ''}`}
              onMouseEnter={() => setHoveredFeature(feature.id)}
              onMouseLeave={() => setHoveredFeature(null)}
            >
              <div className="feature-icon">
                <span className="material-icons">{feature.icon}</span>
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
              <div className="feature-metric">{feature.metric}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Companies Section */}
      <section className="companies">
        <div className="section-header">
          <h2 className="section-title">Analyze Top Companies</h2>
          <p className="section-description">
            Get instant insights from leading tech companies and startups
          </p>
        </div>
        <div className="companies-grid">
          {topCompanies.map((company, index) => (
            <div key={index} className="company-card">
              <div className="company-logo">
                <img
                  src={company.logo}
                  alt={`${company.name} logo`}
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div className="logo-fallback" style={{ display: 'none' }}>
                  <span className="material-icons">business</span>
                </div>
              </div>
              <div className="company-info">
                <h4 className="company-name">{company.name}</h4>
                <p className="company-jobs">{company.jobs}</p>
              </div>
              <div className="company-action">
                <button className="analyze-btn" onClick={onStartAnalyzing}>
                  <span>Analyze</span>
                  <span className="material-icons">arrow_forward</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default LandingPage;