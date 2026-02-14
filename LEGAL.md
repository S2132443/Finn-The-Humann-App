# Licensing & Distribution Compliance

This document tracks licensing, privacy, and regulatory considerations for the Finn Investment Tracker. Review before any commercial distribution.

## Dependency Licensing Matrix

| Dependency | License | Commercial B2B Use | Risk Level | Notes |
|---|---|---|---|---|
| **yfinance** (Yahoo Finance data) | Apache 2.0 (library) / Yahoo ToS (data) | **NO** | **CRITICAL** | Yahoo ToS prohibits commercial use of scraped data. Must replace before selling. |
| **luno-python** (LUNO SDK) | MIT | Yes (SDK) | MEDIUM | SDK is MIT. API ToS: confirm with LUNO for commercial redistribution of ticker data. Per-user API keys for balance sync is fine. |
| **open.er-api.com** (exchange rates) | Custom ToS | Yes | LOW | **Attribution required** (link to ExchangeRate-API on pages showing rates). No redistribution as API. Free tier has no SLA. |
| **ApexCharts** | Dual license | Revenue-dependent | LOW | Free under $2M USD revenue. $199/dev/year above $2M. OEM license ($14,999/year) only if users can customize/build charts. |
| **Alpine.js** | MIT | Yes | NONE | Fully permissive. |
| **Bootstrap 5** | MIT | Yes | NONE | Fully permissive. |
| **FastAPI** | MIT | Yes | NONE | |
| **SQLAlchemy** | MIT | Yes | NONE | |
| **Pydantic** | MIT | Yes | NONE | |
| **httpx** | BSD 3-Clause | Yes | NONE | |

## Critical Blocker: yfinance / Yahoo Finance Data

The `yfinance` library scrapes Yahoo Finance endpoints. Yahoo's Terms of Service explicitly prohibit commercial use:

> "You SHALL NOT sell, lease, share, transfer, or sublicense the Yahoo APIs or access or access codes thereto or derive income from the use or provision of the Yahoo APIs."

The library itself notes it is *"intended for research and educational purposes"* and is *"not affiliated, endorsed, or vetted by Yahoo, Inc."*

### Commercially-Licensed Alternatives

| Provider | Coverage | Pricing | Notes |
|---|---|---|---|
| [Alpha Vantage](https://www.alphavantage.co/) | Global stocks, forex, crypto | Free tier + paid plans | Explicit commercial licensing |
| [Polygon.io](https://polygon.io/) | US + global equities | Pay-as-you-go | Enterprise plans available |
| [Finnhub](https://finnhub.io/) | Global stocks, forex, crypto | Free tier + paid | Commercial plans |
| [EODHD](https://eodhd.com/) | Global exchanges | Paid plans | Explicitly supports commercial use |
| [Financial Modeling Prep](https://site.financialmodelingprep.com/) | Global stocks | Free tier + paid | Commercial plans |

**Action**: Replace `yfinance` with a licensed provider before any commercial distribution.

## LUNO API

- **Public ticker endpoint** (unauthenticated): Generally acceptable for displaying prices. Confirm with LUNO for commercial redistribution.
- **Authenticated API** (balance sync via user's own API keys): Fine — each user authenticates with their own credentials.
- **Rate limit**: 300 calls per minute.
- **Business accounts**: LUNO offers business accounts for commercial integrations.

**Action**: Contact LUNO to confirm commercial use of public ticker data. Consider applying for a LUNO Business account.

## ExchangeRate-API (open.er-api.com)

- Commercial use is **allowed** on both free and paid tiers.
- **Attribution required**: Include a link to ExchangeRate-API on pages displaying rates.
- **No redistribution**: Cannot expose rates as your own API.
- Free tier refreshes once per 24 hours; no SLA.

**Action**: Add attribution link. Consider paid tier for production reliability.

## ApexCharts Licensing

| Your Revenue | License Required | Cost |
|---|---|---|
| Under $2M USD/year | Community (free) | $0 |
| $2M+ USD/year | Commercial | $199/developer/year |
| Users can customize charts | OEM | $14,999/app/year |

A read-only portfolio tracker showing predefined charts does **not** require the OEM license.

**Action**: Track revenue relative to $2M threshold.

---

## Privacy & Data Protection

### Malaysia PDPA (Personal Data Protection Act 2010)

The PDPA applies to processing personal data in commercial transactions, which explicitly includes investment and financing activities. Key requirements:

- **Consent**: Explicit consent required for processing personal data (no "legitimate interests" ground)
- **Data breach notification**: Required under 2024 amendments
- **Data retention**: Financial records must be retained for 6 years (aligned with AMLA and Companies Act)
- **Cross-border transfer**: Personal data cannot be transferred outside Malaysia without adequate protections or consent
- **Data Protection Officer**: Mandatory if processing personal data of 20,000+ individuals or sensitive data of 10,000+ individuals

### GDPR (if serving EU businesses)

- Lawful basis required (consent, contract, legitimate interest)
- Data subject rights: access, rectification, erasure, portability
- Data breach notification within 72 hours
- Data Processing Agreements (DPAs) required with sub-processors
- Privacy Impact Assessments for high-risk processing

### Financial Data Handling

- Investment portfolio data combined with personal identifiers is **sensitive PII**
- External API calls (LUNO, Yahoo Finance, exchange rate API) implicitly reveal portfolio composition to third parties
- No user authentication currently — anyone with access can see all data

---

## Regulatory Considerations

### Malaysia Securities Commission

- A pure **read-only portfolio tracker** (no investment advice, no trade execution) is lower risk and likely does not require a Capital Market Services License (CMSL)
- If the app provides **investment advice** (even automated/algorithmic), a CMSL is required
- Digital assets (crypto) are regulated by the Securities Commission Malaysia
- **Action**: Confirm with a fintech lawyer

### Anti-Money Laundering (AML)

- If the app facilitates transactions or aggregates financial accounts, AML obligations may apply
- Read-only tracking with no transaction execution is lower risk

---

## B2B Readiness Checklist

Required before commercial sale:

- [ ] **Replace yfinance** with commercially-licensed market data provider
- [ ] **Confirm LUNO commercial terms** for public ticker data
- [ ] **Add ExchangeRate-API attribution** (link on pages showing rates)
- [ ] **Implement user authentication** and multi-tenancy (data isolation between customers)
- [ ] **Add encryption at rest** for database (PostgreSQL TDE or application-level)
- [ ] **Enforce HTTPS** (TLS 1.2+) for all connections
- [ ] **Add audit trail logging** for financial data changes
- [ ] **PDPA compliance**: consent management, breach notification procedures, DPA templates
- [ ] **Legal review** by Malaysian fintech lawyer (PDPA + Securities Commission)
- [ ] **Track ApexCharts revenue threshold** ($2M USD)
- [ ] **SOC 2 / ISO 27001** compliance if selling to financial services companies
- [ ] **Data residency**: Ensure financial data stays in Malaysia if required by customers
