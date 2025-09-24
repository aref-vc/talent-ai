import React, { useState } from 'react';
import './LandingPage.css';

const LandingPage = ({ onStartAnalyzing }) => {
  const [hoveredFeature, setHoveredFeature] = useState(null);

  const features = [
    {
      id: 1,
      icon: '📊',
      title: 'Universal Analytics',
      description: '7 comprehensive charts analyzing salary, location, and department distribution across any company',
      metric: '100+ companies supported'
    },
    {
      id: 2,
      icon: '💰',
      title: 'Salary Intelligence',
      description: 'Real-time salary transparency with range detection and competitive benchmarking',
      metric: '$50K-$500K+ range detection'
    },
    {
      id: 3,
      icon: '📍',
      title: 'Location Insights',
      description: 'Geographic distribution analysis with remote work classification and trend tracking',
      metric: '50+ locations tracked'
    },
    {
      id: 4,
      icon: '🎯',
      title: 'Department Analysis',
      description: 'Smart department classification with growth trend analysis and hiring patterns',
      metric: '15+ departments classified'
    },
    {
      id: 5,
      icon: '⚡',
      title: 'Real-time Data',
      description: 'Live job scraping from Greenhouse-powered career pages with instant analytics',
      metric: '<2min processing time'
    },
    {
      id: 6,
      icon: '📈',
      title: 'Competitive Analysis',
      description: 'Compare talent strategies across companies with market positioning insights',
      metric: 'Multi-company benchmarking'
    }
  ];

  const topCompanies = [
    { name: 'OpenAI', logo: '🤖', jobs: '45+ roles' },
    { name: 'Anthropic', logo: '⚡', jobs: '32+ roles' },
    { name: 'Stripe', logo: '💳', jobs: '67+ roles' },
    { name: 'Notion', logo: '📝', jobs: '28+ roles' },
    { name: 'Canva', logo: '🎨', jobs: '89+ roles' },
    { name: 'Ramp', logo: '📊', jobs: '41+ roles' }
  ];

  const analytics = [
    { name: 'Department Distribution', description: 'Interactive doughnut chart showing role distribution' },
    { name: 'Salary Transparency', description: 'Pie chart analyzing salary disclosure patterns' },
    { name: 'Location Analysis', description: 'Bar chart mapping geographic talent distribution' },
    { name: 'Top Paying Roles', description: 'Ranked list of highest compensation positions' },
    { name: 'Role Classification', description: 'Smart categorization with growth metrics' },
    { name: 'Hiring Trends', description: 'Time-series analysis of recruitment patterns' },
    { name: 'Remote Work Index', description: 'Remote vs on-site opportunity breakdown' }
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
            Scrape, analyze, and benchmark talent data from any Greenhouse-powered company.
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
              <span className="cta-icon">🎯</span>
              Start Analyzing
            </button>
            <button className="cta-secondary">
              <span className="cta-icon">📊</span>
              View Demo
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
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
              <div className="feature-metric">{feature.metric}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Analytics Section */}
      <section className="analytics-section">
        <div className="section-header">
          <h2 className="section-title">7 Powerful Analytics Charts</h2>
          <p className="section-description">
            Transform raw job data into actionable insights with our comprehensive analytics suite
          </p>
        </div>
        <div className="analytics-grid">
          {analytics.map((analytic, index) => (
            <div key={index} className="analytic-item">
              <div className="analytic-number">{String(index + 1).padStart(2, '0')}</div>
              <div className="analytic-content">
                <h4 className="analytic-name">{analytic.name}</h4>
                <p className="analytic-description">{analytic.description}</p>
              </div>
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
              <div className="company-logo">{company.logo}</div>
              <div className="company-info">
                <h4 className="company-name">{company.name}</h4>
                <p className="company-jobs">{company.jobs}</p>
              </div>
              <div className="company-action">
                <button className="analyze-btn" onClick={onStartAnalyzing}>
                  Analyze →
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Value Props Section */}
      <section className="value-props">
        <div className="value-prop">
          <div className="prop-icon">💡</div>
          <h3 className="prop-title">Salary Transparency</h3>
          <p className="prop-description">
            Uncover hidden salary data and compensation ranges across any company's entire job catalog
          </p>
        </div>
        <div className="value-prop">
          <div className="prop-icon">📊</div>
          <h3 className="prop-title">Market Insights</h3>
          <p className="prop-description">
            Understand hiring patterns, location strategies, and department growth across industries
          </p>
        </div>
        <div className="value-prop">
          <div className="prop-icon">⚖️</div>
          <h3 className="prop-title">Competitive Analysis</h3>
          <p className="prop-description">
            Benchmark talent strategies and identify opportunities in the competitive landscape
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="final-cta">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Transform Your Talent Intelligence?</h2>
          <p className="cta-description">
            Join HR professionals and talent analysts using Talent AI to make data-driven hiring decisions
          </p>
          <button className="cta-primary large" onClick={onStartAnalyzing}>
            <span className="cta-icon">🚀</span>
            Start Analyzing Now
          </button>
          <p className="cta-note">Free to use • No signup required • Instant results</p>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;