# Finn-The-Humann

A comprehensive investment tracking platform for individuals to monitor portfolio performance and combined net worth. Track true investment returns using TWRR (Time-Weighted Rate of Return) and Modified Dietz calculations.

![Platform Overview](docs/images/dashboard-preview.png)

## Features

### Core Features
1. **Asset, Liability & Net Worth Tracker** - Track overall financial position over time
2. **Asset Allocation** - View actual vs Strategic Asset Allocation (SAA) with variance analysis
3. **TWRR Calculator** - True investment performance measurement
4. **Modified Dietz Returns** - Timing-adjusted portfolio and per-asset-class returns (YTD default)
5. **Total Investment Income** - Track dividends, rental income, interest (with per-asset-class breakdown)
6. **Yield Calculation** - Income yield metrics
7. **Daily Performance Series** - Step-function cumulative return chart for visual tracking

### Additional Features
- **Bulk Price Update** - Update all asset prices/values from a single page
- **P&L Tracking** - Profit & loss with percentage shown on the assets table
- **Per-Asset-Class Returns** - See which asset classes are driving performance
- **Transaction Asset Class Tagging** - Optionally assign cashflows to asset classes for accurate Modified Dietz
- **Multi-Currency Support** - Track assets in any currency, convert to MYR base
- **Monthly Snapshots** - Historical performance tracking
- **PWA Support** - Install as mobile app

## Technology Stack

- **Backend**: FastAPI + SQLAlchemy
- **Templating**: Jinja2 + Bootstrap 5
- **Interactivity**: Alpine.js
- **Database**: PostgreSQL
- **Charts**: ApexCharts (shared JS module)
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
   - Web UI: http://localhost:8000
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

### Database Setup

1. **Create database**
   ```sql
   CREATE DATABASE finn_db;
   ```

2. **Initialize schema**
   ```bash
   psql -U postgres -d finn_db -f database/init.sql
   ```

3. **Run migrations** (for existing databases)
   ```bash
   psql -U postgres -d finn_db -f database/migrations/001_add_altcoin_unit_trust.sql
   psql -U postgres -d finn_db -f database/migrations/002_add_asset_class_id_to_transactions.sql
   ```

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

4. **Start the server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. **Open in browser**
   ```
   http://localhost:8000
   ```

## How to Use

### Quick Start (5 minutes)

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

Go to **Assets > Add Asset** and create entries:

| Asset Name | Symbol | Account | Asset Class | Quantity | Value (RM) |
|------------|--------|---------|-------------|----------|------------|
| Gold Bar | GOLD | My Investment Portfolio | Gold | 1 | 10,000 |
| Apple Inc | AAPL | My Investment Portfolio | US Equities | 50 | 20,000 |
| Cash Reserve | CASH | My Investment Portfolio | Cash | - | 5,000 |
| Bitcoin | BTC | My Investment Portfolio | Bitcoin | 0.5 | 20,000 |
| Maybank | MAYBANK | My Investment Portfolio | MY Equities | 1000 | 40,000 |

Use **Bulk Update** to quickly update all prices from one page.

#### Step 3: Set Strategic Asset Allocation (SAA)

1. Go to **Settings** in the top navbar
2. Click **"Edit SAA"**
3. Enter target percentages for each asset class
4. Set effective date to today
5. Click **Save Allocation**

#### Step 4: Create Historical Snapshots

To see the Net Worth History chart:

1. Go to **Settings > Monthly Snapshots**
2. Click **"Generate Snapshot"**
3. Create snapshots for past months to build history

#### Step 5: Record Income (Optional)

Go to **Income > Record Income** to log dividends, interest, and rental income.

### Accessing from Mobile

#### Same Wi-Fi Network

1. Find your computer's IP address:
   ```cmd
   ipconfig
   ```
   Look for IPv4 Address (e.g., `192.168.1.105`)

2. On your phone, open browser and go to:
   ```
   http://192.168.1.105:8000
   ```

3. Make sure Windows Firewall allows port 8000

#### Using ngrok (Internet Access)

1. Install ngrok from https://ngrok.com
2. Run:
   ```bash
   ngrok http 8000
   ```
3. Use the provided URL (e.g., `https://abc123.ngrok.io`)

### Installing as PWA

#### Desktop (Chrome/Edge)
1. Open http://localhost:8000
2. Click the install icon in address bar
3. Click "Install"

#### Android
1. Open site in Chrome
2. Tap menu > "Add to Home Screen"

#### iOS
1. Open site in Safari
2. Tap Share > "Add to Home Screen"

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
- `PUT /assets/bulk-update` - Bulk update prices, quantities, and values
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
- `GET /returns/modified-dietz` - Calculate Modified Dietz return (YTD default, optional `asset_class_id` filter)
- `GET /returns/daily-series` - Daily cumulative return series for charting
- `GET /income/summary` - Get income summary with per-asset-class breakdown

#### Snapshots
- `GET /snapshots` - List all snapshots
- `POST /snapshots` - Generate new snapshot

#### Settings
- `GET /settings/asset-classes` - List all asset classes
- `GET /settings/currencies` - List exchange rates
- `PUT /settings/currencies` - Update exchange rates

### Interactive Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
Finn-The-Humann-App/
├── docker-compose.yml          # Docker orchestration (db + backend)
├── .env.example                # Environment variables template
├── README.md
│
├── backend/                    # FastAPI application
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # Application entry point
│       ├── config.py           # Configuration settings
│       ├── database.py         # Database connection
│       ├── models/             # SQLAlchemy models
│       │   ├── account.py
│       │   ├── asset.py
│       │   ├── transaction.py
│       │   ├── income.py
│       │   ├── snapshot.py
│       │   ├── allocation.py
│       │   └── currency.py
│       ├── schemas/            # Pydantic schemas
│       ├── api/
│       │   └── v1/             # JSON API endpoints
│       │       ├── accounts.py
│       │       ├── assets.py
│       │       ├── transactions.py
│       │       ├── income.py
│       │       ├── calculations.py
│       │       ├── snapshots.py
│       │       └── settings.py
│       ├── services/           # Business logic (shared)
│       │   └── calculations.py # Net worth, returns, allocation
│       ├── web/                # HTML page routes
│       │   ├── dependencies.py # Templates, flash messages
│       │   ├── dashboard.py
│       │   ├── accounts.py
│       │   ├── assets.py
│       │   ├── transactions.py
│       │   ├── income.py
│       │   └── settings.py
│       ├── templates/          # Jinja2 templates
│       │   ├── base.html
│       │   ├── dashboard.html
│       │   ├── accounts/
│       │   ├── assets/
│       │   ├── transactions/
│       │   ├── income/
│       │   └── settings/
│       └── static/
│           ├── js/charts.js    # Shared chart components
│           ├── manifest.json   # PWA manifest
│           └── sw.js           # Service worker
│
└── database/
    ├── init.sql                # Initial schema + seed data
    └── migrations/             # Incremental migrations
        ├── 001_add_altcoin_unit_trust.sql
        └── 002_add_asset_class_id_to_transactions.sql
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@db:5432/finn_db` |
| `SECRET_KEY` | Application secret key | (required) |
| `BASE_CURRENCY` | Default currency for aggregation | `MYR` |
| `DEBUG` | Enable debug mode | `false` |

### Asset Classes

Default asset classes (configurable via Settings):

| Asset Class | Color | Description |
|-------------|-------|-------------|
| MY Equities | Blue | Malaysian stocks |
| US Equities | Orange | US stocks |
| Gold | Yellow | Gold and precious metals |
| Bitcoin | Orange | Bitcoin |
| Altcoin | Purple | Alternative cryptocurrencies (ETH, SOL, etc.) |
| Cash | Green | Cash and equivalents |
| Fixed Income | Pink | Bonds and fixed income |
| Real Estate | Brown | Property investments |
| Unit Trust | Pink | Unit trust and mutual funds |
| Others | Grey | Uncategorized assets |

## Architecture

The application is a **single FastAPI service** that serves both the JSON API and the web UI:

- **`api/v1/`** - RESTful JSON endpoints for programmatic access
- **`web/`** - HTML page routes using Jinja2 templates
- **`services/`** - Shared business logic used by both API and web routes

This eliminates the need for a separate frontend service. All pages and API endpoints are served from a single process on port 8000.

### Charts

Built with ApexCharts via a shared `FinnCharts` module ([charts.js](backend/app/static/js/charts.js)):

1. **Net Worth Area Chart** - Assets, Liabilities, Net Worth over time
2. **Asset Allocation Donut** - Current portfolio breakdown
3. **Actual vs SAA Bar Chart** - Target vs actual allocation
4. **Income Pie Chart** - Income by type
5. **Daily Return Stepline** - YTD cumulative Modified Dietz return

## Roadmap

- [ ] CSV/Excel file upload and statement parsing
- [ ] User authentication & multi-user support
- [ ] Real-time market data API integration
- [ ] Automatic currency conversion
- [ ] Performance attribution analysis

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on GitHub.

## Acknowledgments

- [ApexCharts](https://apexcharts.com/) for interactive visualizations
- [Bootstrap 5](https://getbootstrap.com/) for responsive UI components
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Alpine.js](https://alpinejs.dev/) for lightweight interactivity
