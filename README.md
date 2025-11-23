# Finn-The-Humann

A comprehensive investment tracking platform for individuals to monitor portfolio performance and combined net worth. Track true investment returns using TWRR (Time-Weighted Rate of Return) and IRR calculations.

![Platform Overview](docs/images/dashboard-preview.png)

## Features

### Core Features (by Priority)
1. **Asset, Liability & Net Worth Tracker** - Track overall financial position over time
2. **Asset Allocation** - View actual vs Strategic Asset Allocation (SAA) with variance analysis
3. **TWRR Calculator** - True investment performance measurement
4. **Total Investment Income** - Track dividends, rental income, interest
5. **Yield Calculation** - Income yield metrics

### Additional Features
- **Performance Attribution** - Understand what's driving returns
- **SAA Optimization** - Strategic asset allocation suggestions
- **Market Performances** - Benchmark comparisons
- **Multi-Currency Support** - Track assets in any currency, convert to MYR base
- **Monthly Snapshots** - Historical performance tracking
- **PWA Support** - Install as mobile app

## Technology Stack

- **Backend**: FastAPI + SQLAlchemy
- **Frontend**: Flask + Jinja2 + Bootstrap 5
- **Database**: PostgreSQL
- **Charts**: ApexCharts
- **Containerization**: Docker Compose

## Quick Start (Docker)

### Prerequisites
- Docker Desktop installed
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Finn-The-Humann-App.git
   cd Finn-The-Humann-App
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:5000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Stopping the Application
```bash
docker-compose down
```

To remove all data (including database):
```bash
docker-compose down -v
```

## Manual Setup (Development)

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Node.js (optional, for frontend tooling)

### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export DATABASE_URL=postgresql://postgres:password@localhost:5432/finn_db
   export SECRET_KEY=your-secret-key
   ```

4. **Run migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start backend server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. **Create virtual environment**
   ```bash
   cd frontend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export API_BASE_URL=http://localhost:8000
   export SECRET_KEY=your-secret-key
   ```

4. **Start frontend server**
   ```bash
   flask run --port 5000
   ```

### Database Setup

1. **Create database**
   ```sql
   CREATE DATABASE finn_db;
   ```

2. **Initialize schema**
   ```bash
   psql -U postgres -d finn_db -f database/init.sql
   ```

## How to Use - Complete Tutorial

This section provides a step-by-step guide to set up your portfolio and generate all dashboard charts.

### Quick Start (5 minutes)

Follow these steps to populate your dashboard with sample data:

#### Step 1: Create Your First Account

1. Go to **Accounts** in the sidebar
2. Click **"Add Account"**
3. Fill in:
   - Name: `My Investment Portfolio`
   - Institution: `Rakuten Trade`
   - Currency: `MYR`
   - Leave "is_liability" unchecked
4. Click **Create Account**

#### Step 2: Add Your Assets

Go to **Assets → Add Asset** and create these entries:

| Asset Name | Symbol | Account | Asset Class | Quantity | Value (RM) |
|------------|--------|---------|-------------|----------|------------|
| Gold Bar | GOLD | My Investment Portfolio | Gold | 1 | 10,000 |
| Apple Inc | AAPL | My Investment Portfolio | US Equities | 50 | 20,000 |
| Cash Reserve | CASH | My Investment Portfolio | Cash | - | 5,000 |
| Bitcoin | BTC | My Investment Portfolio | Bitcoin | 0.5 | 20,000 |
| Maybank | MAYBANK | My Investment Portfolio | MY Equities | 1000 | 40,000 |

**Total Portfolio: RM 95,000**

#### Step 3: Set Strategic Asset Allocation (SAA)

1. Go to **Settings** in the top navbar
2. Click **"Edit SAA"**
3. Enter these target percentages:

| Asset Class | Target % |
|-------------|----------|
| Gold | 10.0 |
| US Equities | 15.0 |
| Cash | 5.0 |
| Bitcoin | 25.0 |
| MY Equities | 45.0 |

4. Set effective date to today
5. Click **Save Allocation**

#### Step 4: Create Historical Snapshots

To see the Net Worth History chart, create snapshots:

1. Go to **Settings → Monthly Snapshots**
2. Create snapshots for these dates:

| Date | (System calculates from your assets) |
|------|-------------------------------------|
| 2025-01-30 | Assets: 90,000, Liabilities: 25,000 |
| 2025-05-03 | Assets: 100,000, Liabilities: 20,000 |

**Note:** For testing, you can temporarily modify asset values before creating each snapshot.

#### Step 5: Record Income (Optional)

Go to **Income → Record Income**:

| Date | Type | Asset | Amount |
|------|------|-------|--------|
| 2025-01-15 | Dividend | Maybank | 500 |
| 2025-02-15 | Dividend | Apple Inc | 200 |
| 2025-03-01 | Interest | Cash Reserve | 50 |

### View Your Dashboard

Return to the **Dashboard** (click Finn logo) to see:

1. **Summary Cards** - Total Assets, Liabilities, Net Worth
2. **Net Worth History** - Area chart showing trends over time
3. **Asset Allocation Pie** - Current portfolio breakdown
4. **Actual vs SAA** - Bar chart comparing your allocation to targets
5. **Income Summary** - Pie chart of income by type

---

### Accessing from Mobile

#### Same Wi-Fi Network

1. Find your computer's IP address:
   ```cmd
   ipconfig
   ```
   Look for IPv4 Address (e.g., `192.168.1.105`)

2. On your phone, open browser and go to:
   ```
   http://192.168.1.105:5000
   ```

3. Make sure Windows Firewall allows port 5000

#### Using ngrok (Internet Access)

1. Install ngrok from https://ngrok.com
2. Run:
   ```bash
   ngrok http 5000
   ```
3. Use the provided URL (e.g., `https://abc123.ngrok.io`)

### Installing as PWA

#### Desktop (Chrome/Edge)
1. Open http://localhost:5000
2. Click the install icon (⊕) in address bar
3. Click "Install"

#### Android
1. Open site in Chrome
2. Tap menu (⋮) → "Add to Home Screen"
3. Tap "Add"

#### iOS
1. Open site in Safari
2. Tap Share (□↑)
3. Tap "Add to Home Screen"

**Note:** PWA installation requires icons in `/static/icons/`. For full functionality, deploy to HTTPS.

---

## Detailed Usage Guide

### Getting Started

1. **Add Accounts**
   - Navigate to "Accounts" → "Add New Account"
   - Enter account name, type (Trading, Savings, Crypto Wallet), and currency
   - Example: "Maybank Trading Account", Type: Trading, Currency: MYR

2. **Add Assets**
   - Navigate to "Assets" → "Add New Asset"
   - Select account, asset class, enter quantity and current value
   - Example: "Apple Stock", Class: US Equities, Value: $5,000

3. **Record Transactions**
   - Navigate to "Transactions" → "Add Transaction"
   - Select account, type (Deposit/Withdrawal), amount, date
   - This is essential for TWRR calculation

4. **Record Income**
   - Navigate to "Income" → "Add Income"
   - Select asset, income type (Dividend/Rental/Interest), amount, date
   - Example: Dividend from Apple, RM 150, Date: 2025-01-15

5. **Set Strategic Allocation**
   - Navigate to "Settings" → "Strategic Asset Allocation"
   - Set target percentages for each asset class
   - Example: MY Equities: 45%, US Equities: 15%, Gold: 10%, Bitcoin: 25%, Cash: 5%

### Dashboard Overview

The main dashboard displays:

- **Net Worth Card** - Current total with trend indicator
- **Net Worth Chart** - Assets, Liabilities, and Net Worth over time
- **Asset Allocation Pie** - Current portfolio breakdown
- **Actual vs SAA Chart** - Comparison with strategic targets
- **TWRR Performance** - Time-weighted returns
- **Income Summary** - Total investment income by type

### Monthly Snapshots

The system automatically captures monthly snapshots of your portfolio for historical tracking. You can also manually trigger a snapshot:

1. Navigate to "Settings" → "Snapshots"
2. Click "Generate Snapshot"
3. Select the period end date

### Understanding TWRR

Time-Weighted Rate of Return (TWRR) measures the compound rate of growth in a portfolio, eliminating the distorting effects of cash flows. This gives you the true performance of your investments.

**Formula:**
```
TWRR = [(1 + R1) × (1 + R2) × ... × (1 + Rn)] - 1
```

Where R1, R2, etc. are the returns for each sub-period between cash flows.

### Multi-Currency Handling

- Assets can be tracked in any currency (USD, SGD, etc.)
- All values are converted to MYR (base currency) for aggregation
- Exchange rates are updated from configuration (future: API integration)

## API Reference

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### Accounts
- `GET /accounts` - List all accounts
- `POST /accounts` - Create new account
- `GET /accounts/{id}` - Get account details
- `PUT /accounts/{id}` - Update account
- `DELETE /accounts/{id}` - Delete account

#### Assets
- `GET /assets` - List all assets
- `POST /assets` - Create new asset
- `GET /assets/{id}` - Get asset details
- `PUT /assets/{id}` - Update asset
- `DELETE /assets/{id}` - Delete asset

#### Transactions
- `GET /transactions` - List all transactions
- `POST /transactions` - Create new transaction
- `GET /transactions/{id}` - Get transaction details

#### Income
- `GET /income` - List all income records
- `POST /income` - Create new income record

#### Calculations
- `GET /networth` - Get current net worth
- `GET /networth/history` - Get net worth history
- `GET /allocation` - Get current asset allocation
- `GET /allocation/comparison` - Get actual vs SAA comparison
- `GET /returns/twrr` - Calculate TWRR
- `GET /income/summary` - Get income summary

#### Snapshots
- `GET /snapshots` - List all snapshots
- `POST /snapshots` - Generate new snapshot

### API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
Finn-The-Humann-App/
├── docker-compose.yml          # Container orchestration
├── .env.example                 # Environment variables template
├── README.md                    # This file
│
├── backend/                     # FastAPI Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/                 # Database migrations
│   └── app/
│       ├── main.py              # Application entry point
│       ├── config.py            # Configuration settings
│       ├── models/              # SQLAlchemy models
│       │   ├── account.py
│       │   ├── asset.py
│       │   ├── transaction.py
│       │   ├── income.py
│       │   └── snapshot.py
│       ├── schemas/             # Pydantic schemas
│       ├── api/
│       │   └── v1/              # Versioned API endpoints
│       │       ├── accounts.py
│       │       ├── assets.py
│       │       ├── transactions.py
│       │       ├── income.py
│       │       └── calculations.py
│       ├── services/            # Business logic
│       │   ├── networth.py
│       │   ├── allocation.py
│       │   ├── twrr.py
│       │   └── income.py
│       └── utils/               # Helpers
│           ├── currency.py
│           └── calculations.py
│
├── frontend/                    # Flask Frontend
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py          # Flask app factory
│       ├── routes/              # Flask blueprints
│       │   ├── dashboard.py
│       │   ├── accounts.py
│       │   ├── assets.py
│       │   └── settings.py
│       ├── templates/           # Jinja2 templates
│       │   ├── base.html
│       │   ├── dashboard.html
│       │   └── components/
│       └── static/
│           ├── css/
│           ├── js/
│           ├── manifest.json    # PWA manifest
│           └── sw.js            # Service worker
│
└── database/
    └── init.sql                 # Initial schema
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@db:5432/finn_db` |
| `SECRET_KEY` | Application secret key | (required) |
| `API_BASE_URL` | Backend API URL | `http://backend:8000` |
| `BASE_CURRENCY` | Default currency for aggregation | `MYR` |
| `DEBUG` | Enable debug mode | `false` |

### Asset Classes

Default asset classes (configurable via database):
- MY Equities
- US Equities
- Gold
- Bitcoin/Crypto
- Cash
- Fixed Income
- Real Estate

## Charts & Visualizations

Built with ApexCharts:

1. **Net Worth Area Chart** - Assets, Liabilities, Net Worth over time
2. **Asset Allocation Pie/Donut** - Current portfolio breakdown
3. **Actual vs SAA Grouped Bar** - Target vs actual allocation
4. **Allocation History Stacked Bar** - Multi-year trends
5. **TWRR Line Chart** - Performance over time
6. **Income Bar Chart** - Income by type and period

All charts are:
- Interactive with tooltips
- Responsive for mobile
- Exportable as PNG/SVG
- Consistently color-coded

## PWA (Progressive Web App)

The application can be installed as a mobile app:

1. Open the application in mobile browser
2. Tap "Add to Home Screen" (iOS) or install prompt (Android)
3. The app will work offline with cached data

## Roadmap

### Phase 2 - Data Import
- [ ] CSV/Excel file upload
- [ ] Statement parsing (PDF)
- [ ] Automatic data extraction

### Phase 3 - Advanced Features
- [ ] User authentication & multi-user support
- [ ] Real-time market data API integration
- [ ] Automatic currency conversion
- [ ] Performance attribution analysis
- [ ] Monte Carlo retirement projections

### Phase 4 - B2B Features
- [ ] Multi-tenant architecture
- [ ] Admin dashboard
- [ ] Client management
- [ ] White-labeling support
- [ ] Billing integration

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on GitHub or contact the development team.

## Acknowledgments

- ApexCharts for beautiful visualizations
- Bootstrap 5 for responsive UI components
- FastAPI for high-performance backend
- Flask for flexible frontend templating
