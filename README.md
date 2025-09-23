# 🎯 Talent AI - Universal Job Scraping & Intelligence Platform

A powerful, universal job scraping and talent intelligence platform that works with any Greenhouse-powered career page. Built with the same technology used for OpenAI and Anthropic talent analysis.

## ✨ Features

- **Universal Scraping**: Works with any Greenhouse job board URL
- **Salary Detection**: Automatically extracts salary ranges from job postings
- **Rich Analytics**: Department distribution, location analysis, salary transparency metrics
- **Interactive Dashboard**: Real-time data visualization with Chart.js
- **Export Options**: Download data in JSON or CSV format
- **Recent Companies**: Track and reload previously scraped companies
- **Fast & Reliable**: Powered by Playwright for robust web scraping

## 🚀 Quick Start

### One-Command Launch

```bash
./start.sh
```

This will:
1. Install all dependencies (Python & Node.js)
2. Start the backend API on port 8100
3. Start the frontend on port 3100
4. Open your browser to the application

### Manual Installation

#### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn app:app --host 0.0.0.0 --port 8100 --reload
```

#### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## 📊 Usage

1. **Open the App**: Navigate to http://localhost:3100
2. **Enter URL**: Paste a Greenhouse job board URL (e.g., `https://job-boards.greenhouse.io/openai`)
3. **Start Scraping**: Click "Start Scraping" and wait for results
4. **View Analytics**: Explore job listings, salary data, and visualizations
5. **Export Data**: Download results in JSON or CSV format

## 🏢 Example Companies

The platform includes quick-start buttons for popular companies:
- OpenAI
- Anthropic
- Stripe
- Coinbase
- Discord
- Figma

## 🔧 Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Playwright**: Browser automation for web scraping
- **BeautifulSoup**: HTML parsing and data extraction
- **Pandas**: Data manipulation and CSV export

### Frontend
- **React**: Modern UI framework
- **Chart.js**: Interactive data visualizations
- **Axios**: HTTP client for API communication
- **JetBrains Mono**: Beautiful monospace font

## 📁 Project Structure

```
Talent AI/
├── backend/
│   ├── app.py           # FastAPI application
│   ├── scraper.py        # Universal Greenhouse scraper
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── App.js        # Main application
│   │   └── App.css       # Styling
│   └── package.json      # Node.js dependencies
├── data/                 # Scraped data storage
├── start.sh             # One-command launcher
└── README.md            # This file
```

## 🎨 Features in Detail

### Salary Intelligence
- Automatically detects salary ranges in multiple formats
- Calculates disclosure rates
- Shows average compensation ranges

### Department Analysis
- Visualizes department distribution with doughnut charts
- Identifies hiring focus areas
- Tracks team growth patterns

### Geographic Distribution
- Maps job locations globally
- Identifies concentration areas
- Supports remote position tracking

### Export Capabilities
- **JSON**: Complete data with all metadata
- **CSV**: Spreadsheet-compatible format
- Preserves all scraped information

## 🛠️ API Endpoints

- `POST /scrape` - Scrape a company's job listings
- `GET /companies` - List all scraped companies
- `GET /analytics/{company}` - Get company analytics
- `GET /export/{company}` - Export company data
- `GET /docs` - Interactive API documentation

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill processes on ports
lsof -ti:8100 | xargs kill
lsof -ti:3100 | xargs kill
```

### Playwright Issues
```bash
# Reinstall browser binaries
playwright install chromium
```

### Dependencies Not Found
```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
rm -rf node_modules package-lock.json
npm install
```

## 📈 Performance

- Scrapes 100+ jobs in ~30 seconds
- Handles pagination automatically
- Retries on network failures
- Caches results for quick reloading

## 🔒 Privacy & Ethics

- Only scrapes publicly available job postings
- Respects robots.txt and rate limits
- No personal data collection
- Complies with website terms of service

## 🚦 System Requirements

- Python 3.8+
- Node.js 16+
- 4GB RAM minimum
- Chrome/Chromium browser

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new scraper patterns
- Improve salary detection
- Add new visualizations
- Enhance the UI/UX

## 🎯 Future Enhancements

- [ ] Support for more job board platforms
- [ ] Advanced filtering and search
- [ ] Historical trend analysis
- [ ] Email alerts for new positions
- [ ] Company comparison features
- [ ] Skills extraction and analysis
- [ ] Integration with LinkedIn
- [ ] Mobile responsive design

---

Built with ❤️ using the same technology that powers OpenAI and Anthropic talent analysis dashboards.