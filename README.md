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
- **One-Click Price Refresh** - Fetch latest prices from LUNO and Yahoo Finance with a single button
- **Market Page** - Track price movements for portfolio holdings and watchlist symbols
- **Broker Sync** - Auto-import balances from connected brokerages (LUNO supported, extensible to others)
- **Bulk Price Update** - Update all asset prices/values from a single page
- **P&L Tracking** - Profit & loss with percentage shown on the assets table
- **Auto Exchange Rates** - Update all currency rates from a free API on demand
- **Per-Asset-Class Returns** - See which asset classes are driving performance
- **Transaction Asset Class Tagging** - Optionally assign cashflows to asset classes for accurate Modified Dietz
- **Multi-Currency Support** - Track assets in any currency, convert to MYR base
- **Monthly Snapshots** - Historical performance tracking
- **PWA Support** - Install as mobile app

### Supported Data Sources

| Data Source | Asset Classes | How It Works |
|-------------|---------------|--------------|
| **LUNO API** | Bitcoin, Altcoin | Fetches all MYR pairs in one call (BTC, ETH, XRP, SOL, ADA, LINK, UNI, LTC, BCH, POL, AVAX, ATOM, NEAR, ALGO) |
| **Yahoo Finance** | MY Equities, US Equities, Gold | Batch fetch via `yfinance`. MY stocks auto-append `.KL` suffix. Gold converts USD/oz to MYR/gram |
| **LUNO Authenticated API** | Bitcoin, Altcoin | Optional: auto-import wallet balances via API key (no manual quantity entry) |
| **Exchange Rate API** | All currencies | Free API updates USD, SGD, EUR, GBP, JPY, AUD, CNY rates to MYR |
| **Manual** | Unit Trust, Others | No free API available; use Bulk Update page |

## Technology Stack

- **Backend**: FastAPI + SQLAlchemy, serving both `/api/v1/*` and the built SPA from one process
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS + shadcn/ui + TanStack Query + Recharts
- **PWA**: `vite-plugin-pwa` (Workbox) — installable on desktop and mobile, offline shell
- **Database**: PostgreSQL
- **Price Data**: LUNO API + yfinance
- **Broker Sync**: luno-python SDK (extensible provider pattern)
- **Containerization**: Docker Compose (multi-stage build: Node → Python)

## Quick Start (one-time local install)

### Prerequisites
- Docker Desktop
- Git

### Installation

```bash
git clone https://github.com/yourusername/Finn-The-Humann-App.git
cd Finn-The-Humann-App
cp .env.example .env
docker-compose up --build
```

Then:

- **On your PC**: open http://localhost:8000
- **On your phone** (same Wi-Fi): find your PC's IPv4 with `ipconfig` (e.g. `192.168.1.105`), open `http://192.168.1.105:8000` in Chrome/Safari, then **Add to Home Screen** — installs as a PWA with offline shell.
- **API docs**: http://localhost:8000/docs

### Stopping

```bash
docker-compose down          # stop
docker-compose down -v       # stop + wipe database
```

## Development

Two-process dev loop with hot-reload on both sides:

```bash
# Terminal 1 — backend + db
docker-compose up db
uvicorn app.main:app --reload --port 8000   # from backend/

# Terminal 2 — frontend
cd frontend
npm install
npm run dev                                  # http://localhost:3000, proxies /api to :8000
```

Vite's dev server listens on `0.0.0.0` so you can also hit `http://<pc-ip>:3000` from your phone during development.

## Manual Setup (without Docker)

### Prerequisites
- Python 3.11+, PostgreSQL 15+, Node 20+

```bash
# Database
createdb finn_db
psql -U postgres -d finn_db -f database/init.sql
for f in database/migrations/*.sql; do psql -U postgres -d finn_db -f "$f"; done

# Backend
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://postgres:password@localhost:5432/finn_db
export SECRET_KEY=change-me
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run build    # produces frontend/dist/ which FastAPI will serve
```

Open http://localhost:8000. For hot-reload frontend dev, run `npm run dev` on :3000 instead of building.

## How to Use

### Quick Start (5 minutes)

#### Step 1: Create Accounts

Go to **Accounts > Add Account** and create one per institution:

| Account Name | Institution | Type | Currency |
|-------------|-------------|------|----------|
| Maybank Gold | Maybank | Savings Account | MYR |
| Moomoo | Moomoo | Trading Account | MYR |
| Maybank Unit Trust | Maybank | Savings Account | MYR |
| LUNO | LUNO | Crypto Wallet | MYR |

#### Step 2: Add Your Assets

Go to **Assets > Add Asset** and create entries. The **symbol** field is important for automatic price fetching:

| Asset Name | Symbol | Account | Asset Class | Quantity |
|------------|--------|---------|-------------|----------|
| Gold Savings | XAUUSD | Maybank Gold | Gold | 10 |
| Maybank Shares | 1155 | Moomoo | MY Equities | 1000 |
| Apple Inc | AAPL | Moomoo | US Equities | 50 |
| Bitcoin | BTC | LUNO | Bitcoin | 0.5 |
| Ethereum | ETH | LUNO | Altcoin | 5 |
| Solana | SOL | LUNO | Altcoin | 100 |
| Unit Trust Fund | - | Maybank Unit Trust | Unit Trust | 5000 |

#### Step 3: Fetch Prices

Click **"Refresh Prices"** on the Assets page or visit the **Market** page and click **"Refresh Prices"**. This fetches live prices from LUNO and Yahoo Finance and updates all assets automatically.

#### Step 4: Set Strategic Asset Allocation (SAA)

1. Go to **Settings** in the top navbar
2. Click **"Edit SAA"**
3. Enter target percentages for each asset class
4. Set effective date to today
5. Click **Save Allocation**

#### Step 5: Create Historical Snapshots

To see the Net Worth History chart:

1. Go to **Settings > Monthly Snapshots**
2. Click **"Generate Snapshot"**
3. Create snapshots for past months to build history

#### Step 6: Record Income (Optional)

Go to **Income > Record Income** to log dividends, interest, and rental income.

### Market Page

The **Market** page (`/market`) shows all tracked symbols with:
- Current price and price change since last refresh
- Green/red indicators for price movement
- Owned quantity and value for portfolio holdings
- Watchlist symbols you don't own but want to track

You can add any symbol to the watchlist from the Market page using the **"Add Symbol"** button.

### Broker Integrations (Optional)

Connect your brokerage accounts to auto-import balances instead of entering them manually. Currently supported: **LUNO**.

#### Setting Up LUNO Sync

1. Go to [LUNO API Keys](https://www.luno.com/wallet/security/api_keys) and create a **read-only** API key
2. Add to your `.env` file:
   ```
   LUNO_API_KEY_ID=your_key_id
   LUNO_API_KEY_SECRET=your_key_secret
   ```
3. Restart the application
4. Go to **Settings** → "Broker Integrations" card shows LUNO as "Connected"
5. Click **"Sync Balances"** to auto-import all your LUNO crypto holdings

The sync will:
- Auto-create a LUNO account if one doesn't exist
- Create assets for each coin with balance > 0 (BTC, ETH, SOL, etc.)
- Update quantities for existing assets
- Zero out assets that no longer have balance
- Auto-register symbols for price tracking on the Market page

You can also sync from the **Market** page using the **"Sync LUNO"** button.

#### Adding More Brokers

The app uses a provider-based architecture. Each broker is a separate module in `services/brokers/`. See [LEGAL.md](LEGAL.md) for licensing considerations when adding new data sources.

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

#### Prices
- `POST /prices/refresh` - Fetch latest prices from LUNO + Yahoo Finance, update exchange rates, and push to portfolio assets

#### Market (Watchlist)
- `GET /market` - List all tracked symbols with prices and owned quantities
- `POST /market` - Add a symbol to the watchlist
- `DELETE /market/{symbol}` - Remove a symbol from the watchlist

#### Brokers
- `GET /brokers` - List all registered broker providers with configuration status
- `POST /brokers/{provider}/sync` - Sync balances from a specific broker (e.g., `luno`)

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
├── LEGAL.md                    # Licensing & distribution compliance
│
├── backend/                    # FastAPI — API + serves the built SPA
│   ├── Dockerfile              # Multi-stage: Node build → Python runtime
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # Entry point + SPA catch-all
│       ├── config.py
│       ├── database.py
│       ├── models/             # SQLAlchemy
│       ├── schemas/            # Pydantic
│       ├── api/v1/             # JSON endpoints (accounts, assets, transactions,
│       │                       # income, calculations, snapshots, settings,
│       │                       # prices, brokers)
│       └── services/           # Shared business logic
│           ├── calculations.py
│           ├── price_fetcher.py
│           └── brokers/        # Provider pattern (luno.py, extensible)
│
├── frontend/                   # React 19 + Vite + TS SPA
│   ├── index.html
│   ├── vite.config.ts          # Dev proxy /api → :8000, PWA plugin
│   ├── public/                 # Favicon + PWA icons
│   └── src/
│       ├── main.tsx, App.tsx
│       ├── lib/api.ts          # Typed ApiClient (fetch)
│       ├── hooks/              # TanStack Query hooks per resource
│       ├── pages/              # Dashboard, Accounts, Assets, Market,
│       │                       # Transactions, Income, Settings
│       ├── components/charts/  # Recharts wrappers
│       ├── components/layout/  # Sidebar, MobileNav
│       ├── components/ui/      # shadcn primitives
│       └── types/api.ts        # Payload interfaces
│
└── database/
    ├── init.sql                # Initial schema + seed data
    └── migrations/
        ├── 001_add_altcoin_unit_trust.sql
        ├── 002_add_asset_class_id_to_transactions.sql
        └── 003_add_market_prices.sql
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@db:5432/finn_db` |
| `SECRET_KEY` | Application secret key | (required) |
| `BASE_CURRENCY` | Default currency for aggregation | `MYR` |
| `DEBUG` | Enable debug mode | `false` |
| `LUNO_API_KEY_ID` | LUNO API key ID (optional) | (empty) |
| `LUNO_API_KEY_SECRET` | LUNO API key secret (optional) | (empty) |

### Asset Classes

Default asset classes (configurable via Settings):

| Asset Class | Color | Price Source |
|-------------|-------|-------------|
| MY Equities | Blue | Yahoo Finance (`.KL` suffix) |
| US Equities | Orange | Yahoo Finance |
| Gold | Yellow | Yahoo Finance (`GC=F` → MYR/gram) |
| Bitcoin | Orange | LUNO API |
| Altcoin | Purple | LUNO API |
| Cash | Green | Manual |
| Fixed Income | Pink | Manual |
| Real Estate | Brown | Manual |
| Unit Trust | Pink | Manual |
| Others | Grey | Manual |

## Architecture

The application is a **single FastAPI service** that serves both the JSON API and the web UI:

- **`api/v1/`** - RESTful JSON endpoints for programmatic access
- **`web/`** - HTML page routes using Jinja2 templates
- **`services/`** - Shared business logic used by both API and web routes

This eliminates the need for a separate frontend service. All pages and API endpoints are served from a single process on port 8000.

### Price Refresh Flow

1. User clicks **"Refresh Prices"** (on Assets, Bulk Update, or Market page)
2. `POST /api/v1/prices/refresh` is called
3. Exchange rates are updated first (so currency conversions use fresh rates)
4. `price_fetcher.py` queries `market_prices` table to know what symbols to fetch
5. Prices are fetched from LUNO (crypto) and Yahoo Finance (stocks, gold) in parallel groups
6. `market_prices` table is updated (current → previous, new → current, change % calculated)
7. Matching portfolio `assets` are updated (price + value recalculated)
8. UI reloads to show fresh data

### Broker Sync Flow

1. User clicks **"Sync Balances"** (on Settings or Market page)
2. `POST /api/v1/brokers/{provider}/sync` is called
3. Provider fetches balances from external API (e.g., LUNO `get_balances()`)
4. For each asset with balance > 0: find or create asset in portfolio
5. Auto-create `market_prices` rows for new symbols (for price tracking)
6. Return summary: created, updated, zeroed counts

The provider pattern means adding a new broker requires only one new file in `services/brokers/` — no changes to API endpoints, UI templates, or existing logic.

### Charts

Built with ApexCharts via a shared `FinnCharts` module ([charts.js](backend/app/static/js/charts.js)):

1. **Net Worth Area Chart** - Assets, Liabilities, Net Worth over time
2. **Asset Allocation Donut** - Current portfolio breakdown
3. **Actual vs SAA Bar Chart** - Target vs actual allocation
4. **Income Pie Chart** - Income by type
5. **Daily Return Stepline** - YTD cumulative Modified Dietz return

## Roadmap

- [ ] Scheduled automatic price updates (APScheduler)
- [ ] Automated monthly snapshots
- [ ] CSV/Excel file upload and statement parsing
- [ ] User authentication & multi-user support
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
- [LUNO API](https://www.luno.com/en/developers/api) for Malaysian crypto prices
- [yfinance](https://github.com/ranaroussi/yfinance) for stock and gold price data
