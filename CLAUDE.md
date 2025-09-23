# Claude Code Configuration - Talent AI

## Project Overview

**Talent AI** is a universal job scraping and intelligence platform that extracts, analyzes, and visualizes talent data from Greenhouse-powered career pages. This configuration helps Claude understand the project structure, coding standards, and development workflow.

## Quick Commands

### Start Application
```bash
./start.sh
```

### Development Commands
```bash
# Backend only
cd backend && source venv/bin/activate && uvicorn app:app --reload --port 8100

# Frontend only
cd frontend && PORT=3100 npm start

# Kill processes
lsof -ti:8100 | xargs kill -9
lsof -ti:3100 | xargs kill -9
```

### Testing Commands
```bash
# Test scraper with specific company
cd backend && python scraper.py

# Test API endpoints
curl http://localhost:8100/docs
```

## Project Structure

```
/Users/aref/Documents/Claude Code/Talent AI/
├── backend/               # Python/FastAPI backend
│   ├── app.py            # Main API application
│   ├── scraper.py        # Greenhouse scraper engine
│   └── requirements.txt  # Python dependencies
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   └── App.js       # Main React app
│   └── package.json     # Node dependencies
├── data/                # JSON data storage
└── start.sh            # Quick start script
```

## Key Features to Maintain

### 1. Universal Scraping Engine
- **Location**: `backend/scraper.py`
- **Key Methods**:
  - `scrape_greenhouse_jobs()` - Main scraping function
  - `parse_job_element()` - Extracts job data from HTML
  - `extract_salary()` - Parses salary information
  - `scrape_job_details()` - Fetches individual job pages

### 2. Smart Data Extraction
- Extracts locations from parentheses in job titles
- Infers departments from job titles when not available
- Supports multiple salary formats ($XXXk, $XXX,XXX, etc.)
- Handles various Greenhouse HTML structures

### 3. Analytics Engine
- Department distribution (doughnut chart)
- Location analysis (bar chart)
- Salary transparency metrics (pie chart)
- Export to JSON/CSV formats

## Coding Standards

### Python (Backend)
```python
# Use type hints
async def scrape_greenhouse_jobs(self, company_url: str, fetch_details: bool = True) -> List[Dict]:

# Use descriptive variable names
job_elements = await page.query_selector_all('.opening')

# Handle errors gracefully
try:
    jobs = await scraper.scrape_greenhouse_jobs(url)
except Exception as e:
    logger.error(f"Scraping failed: {e}")
    return {"error": str(e)}
```

### JavaScript (Frontend)
```javascript
// Use functional components with hooks
function JobsTable({ jobs }) {
  const [filter, setFilter] = useState('');

// Use descriptive component names
<SearchPanel onScrape={handleScrape} />

// Handle loading states
{loading ? <Spinner /> : <Results />}
```

### CSS Styling
```css
/* Use CSS variables for theming */
:root {
  --primary: hsl(17, 82%, 54%);
  --background: hsl(30, 6%, 14%);
}

/* Use semantic class names */
.search-panel { }
.job-table { }
.analytics-dashboard { }
```

## Color Palette

```css
--primary: hsl(17, 82%, 54%)      /* Orange - CTAs, highlights */
--secondary: hsl(34, 6%, 23%)     /* Dark brown - secondary elements */
--accent: hsl(39, 18%, 76%)       /* Beige - text secondary */
--background: hsl(30, 6%, 14%)    /* Dark brown - main background */
--foreground: hsl(45, 100%, 97%)  /* Off-white - primary text */
--card: hsl(30, 5%, 16%)          /* Card backgrounds */
--border: hsl(34, 6%, 23%)        /* Borders */
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/scrape` | POST | Scrape company jobs |
| `/companies` | GET | List scraped companies |
| `/analytics/{company}` | GET | Get company analytics |
| `/export/{company}` | GET | Export data (JSON/CSV) |
| `/docs` | GET | API documentation |

## Common Issues & Solutions

### Issue: "Not specified" appearing in results
**Solution**: The scraper uses multiple methods to extract location/department:
1. Check for specific CSS selectors
2. Parse from text patterns
3. Extract from job title (parentheses)
4. Infer from keywords

### Issue: No salary data
**Solution**: The scraper:
1. First checks the job listing
2. Then fetches job detail page (up to 20 jobs)
3. Searches for various salary patterns

### Issue: Slow scraping
**Solution**:
- Limit detail fetches: `max_detail_fetches=10`
- Use concurrent processing
- Cache results in `data/` directory

## Testing Checklist

When making changes, ensure:

- [ ] Scraper works with OpenAI, Anthropic, Stripe (test companies)
- [ ] Location extraction from parentheses works
- [ ] Department inference from job titles works
- [ ] Salary patterns are correctly parsed
- [ ] Export to JSON/CSV produces valid files
- [ ] Charts render correctly with data
- [ ] Quick-start buttons populate form correctly
- [ ] Recent companies list updates after scraping

## Deployment Notes

### Ports
- Frontend: 3100
- Backend: 8100

### Dependencies
- Python 3.8+
- Node.js 16+
- Playwright (Chromium)

### Environment Setup
```bash
# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Frontend
npm install
```

## Future Enhancements

### Priority 1 (Next Release)
- [ ] Add more job board platforms (Lever, Workday)
- [ ] Implement database storage (PostgreSQL)
- [ ] Add user authentication
- [ ] Create company comparison view

### Priority 2
- [ ] Machine learning for salary prediction
- [ ] Historical trend analysis
- [ ] Email notifications for new jobs
- [ ] Advanced search filters

### Priority 3
- [ ] Mobile app (React Native)
- [ ] API rate limiting
- [ ] Webhook support
- [ ] Data export scheduler

## Git Workflow

### Commit Messages
Use conventional commits:
```
feat: Add salary range detection
fix: Handle empty location fields
docs: Update API documentation
style: Format code with black
refactor: Optimize scraping pipeline
```

### Branch Naming
```
feature/add-lever-support
fix/location-parsing-issue
refactor/scraper-optimization
```

## Performance Metrics

Target performance:
- Scraping: <1 second per job
- API response: <100ms
- Frontend load: <2 seconds
- Memory usage: <300MB

## Support & Documentation

- Main README: `/README.md`
- Architecture: `/ARCHITECTURE.md`
- API Docs: `http://localhost:8100/docs`
- Frontend: `http://localhost:3100`

## Claude Code Settings

When working on this project:

1. **Always use the color palette variables** - Never hardcode colors
2. **Maintain JetBrains Mono font** - It's part of the brand
3. **Test with real companies** - Use the quick-start pack
4. **Preserve smart extraction logic** - Location/department/salary parsing is critical
5. **Keep the UI dark theme** - Matches the earth-tone color scheme

## Debug Mode

Enable detailed logging:
```python
# backend/app.py
logging.basicConfig(level=logging.DEBUG)

# backend/scraper.py
logger.setLevel(logging.DEBUG)
```

View browser during scraping:
```python
# backend/scraper.py
self.browser = await playwright.chromium.launch(
    headless=False,  # Change to False
    args=['--no-sandbox', '--disable-dev-shm-usage']
)
```

---

This configuration ensures consistent development and maintenance of Talent AI across Claude Code sessions.