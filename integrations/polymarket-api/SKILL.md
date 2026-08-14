---
name: polymarket-api
description: Use when querying Polymarket Gamma/CLOB trading APIs.
trigger: Use when coding against Polymarket APIs — fetching markets, placing orders, building scanners.
---
# Polymarket API Reference Skill

## Base URLs
| API | Base URL | Purpose |
|-----|----------|---------|
| **Gamma** | `https://gamma-api.polymarket.com` | Public market/event metadata, search, tags, series, sports |
| **CLOB** | `https://clob.polymarket.com` | Order book, midpoints, trading (authenticated) |
| **Data** | `https://data-api.polymarket.com` | Historical prices, klines, funding, index |
| **Bridge** | `https://bridge-api.polymarket.com` | Deposits/withdrawals, asset bridging |
| **Relayer** | `https://relayer-api.polymarket.com` | Order submission, cancellation, proxy management |

---

## Gamma API (Public — No Auth Required)

### Events
| Endpoint | Method | Params | Use Case |
|----------|--------|--------|----------|
| `/events/{id}` | GET | `id` (string) | Fetch single event by ID |
| `/events/slug/{slug}` | GET | `slug` (string) | Fetch event by slug |
| `/events/keyset` | GET | `closed`, `limit`, `after_cursor`, `tag_id` | Paginated event list (cursor-based) |
| `/events` | GET | `closed`, `limit`, `offset` | Legacy offset pagination |

**Response:** `Event` object with `markets[]` array. Each market has `clobTokenIds` (JSON string array of YES/NO token IDs).

### Markets
| Endpoint | Method | Params | Use Case |
|----------|--------|--------|----------|
| `/markets/{id}` | GET | `id` (string) | Fetch single market |
| `/markets/slug/{slug}` | GET | `slug` (string) | Fetch market by slug |
| `/markets/keyset` | GET | `closed`, `limit`, `after_cursor`, `tag_id`, `sports_market_types` | Paginated market list |
| `/markets` | GET | `closed`, `limit`, `offset` | Legacy offset pagination |

**Key Market Fields:**
- `conditionId` — onchain condition ID (hex)
- `clobTokenIds` — `"[\"YES_TOKEN_ID\", \"NO_TOKEN_ID\"]"` (JSON string)
- `outcomePrices` — `"[\"0.49\", \"0.51\"]"` (JSON string)
- `volume`, `liquidity`, `openInterest` — numeric strings
- `bestBid`, `bestAsk`, `lastTradePrice` — current prices
- `enableOrderBook` — boolean, whether CLOB trading is enabled
- `feeType` — e.g., `politics_fees`, `sports_fees_v2`
- `feeSchedule` — `{exponent, rate, takerOnly, rebateRate}`

### Series
| Endpoint | Method | Params |
|----------|--------|--------|
| `/series/{id}` | GET | `id` (string) |
| `/series` | GET | `recurrence`, `closed`, `limit` |

### Sports
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/sports` | GET | List sports with tag mappings |
| `/sports/market-types` | GET | Valid `sportsMarketTypes` for filtering |

### Tags
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/tags` | GET | List all tags (paginated) |
| `/tags/slug/{slug}` | GET | Resolve tag slug → numeric ID |
| `/tags/slug/{slug}/related-tags` | GET | Relationship records |
| `/tags/slug/{slug}/related-tags/tags` | GET | Full related tag objects |

### Search
| Endpoint | Method | Params |
|----------|--------|--------|
| `/public-search` | GET | `q` (query), `page_size` |

---

## CLOB API (Authenticated — Requires Proxy/API Key)

### Authentication
1. **Create Proxy** — `POST /create-proxy` (EOA signature) → returns `apiKey`, `apiSecret`, `apiPassphrase`
2. **Use Proxy** — Sign requests with proxy key (see `proxy signing` in docs)

### Market Data (Public)
| Endpoint | Method | Params | Returns |
|----------|--------|--------|---------|
| `/book` | GET | `token_id` | `{bids: [{price, size}], asks: [{price, size}]}` |
| `/midpoint` | GET | `token_id` | `{mid: "0.495"}` |
| `/bbo` | GET | — | Best bid/offer for all instruments |
| `/instruments` | GET | — | All tradeable instruments with metadata |

### Trading (Authenticated)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/orders` | POST | Create order (requires proxy sig) |
| `/orders` | DELETE | Cancel orders (requires proxy sig) |
| `/orders/coid` | DELETE | Cancel by client order ID |
| `/open-orders` | GET | List open orders |
| `/fills` | GET | Fill history |
| `/positions` | GET | Current positions |
| `/balances` | GET | Asset balances |
| `/equity` | GET | Equity history |

### Account
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/credentials` | GET | Account ID, address, proxy keys |
| `/stats` | GET | 7-day trading stats |
| `/limits` | GET | Rate-limit tier allowances |
| `/activity` | GET | User activity (trades, positions) |

---

## Python Client Patterns (from `py-clob-client`)

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType

# Public client (no auth) — for reading books, midpoints
client = ClobClient(host="https://clob.polymarket.com")

# Get order book
book = client.get_book(token_id="12345...")

# Get midpoint
mid = client.get_midpoint(token_id="12345...")

# Authenticated client — for placing orders
client = ClobClient(
    host="https://clob.polymarket.com",
    key=API_KEY,
    secret=API_SECRET,
    passphrase=API_PASSPHRASE,
)
# Or use proxy:
client.set_proxy(proxy_address, proxy_key)

# Place order
order = OrderArgs(
    token_id="12345...",
    price=0.50,
    size=100.0,
    side="BUY",
    order_type=OrderType.GTC,
)
resp = client.create_order(order)
```

---

## Gamma API Pagination (Keyset)

**Always use keyset pagination** — `offset` is rejected.

```python
import httpx

async def fetch_all_markets(tag_id=None, closed=False):
    url = "https://gamma-api.polymarket.com/markets/keyset"
    params = {"closed": str(closed).lower(), "limit": 500}
    if tag_id:
        params["tag_id"] = tag_id
    
    all_markets = []
    async with httpx.AsyncClient() as client:
        while True:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            all_markets.extend(data.get("markets", []))
            cursor = data.get("next_cursor")
            if not cursor:
                break
            params["after_cursor"] = cursor
    return all_markets
```

---

## Key Response Schemas

### Event
```json
{
  "id": "90177",
  "slug": "will-the-us-confirm-that-aliens-exist-before-2027",
  "title": "Will the US confirm that aliens exist by...?",
  "markets": [
    {
      "id": "703257",
      "question": "Will the US confirm that aliens exist before 2027?",
      "conditionId": "0x747dc809fb79e1b05be09c42d6179459a58de2ef3e40f02484a4e1260f741f75",
      "clobTokenIds": "[\"YES_TOKEN_ID\", \"NO_TOKEN_ID\"]",
      "outcomePrices": "[\"0.055\", \"0.945\"]",
      "volume": "36298756.528",
      "liquidity": "568922.6944",
      "bestBid": 0.05,
      "bestAsk": 0.06,
      "enableOrderBook": true
    }
  ]
}
```

### Market (from `/markets/keyset`)
```json
{
  "id": "741099",
  "question": "Will LeBron James retire before next NBA season?",
  "conditionId": "0x73057b771600660ac6e659c5b831587fd3bdd378e63f359731aa3e1538577fb0",
  "clobTokenIds": "[\"938993...\", \"372197...\"]",
  "outcomePrices": "[\"0.008\", \"0.992\"]",
  "volume": "287826.664",
  "liquidity": "6025.16569",
  "bestBid": 0.005,
  "bestAsk": 0.011,
  "enableOrderBook": true,
  "feeType": "sports_fees_v2",
  "feeSchedule": {"exponent": 1, "rate": 0.05, "takerOnly": true, "rebateRate": 0.15}
}
```

### Order Book (`/book?token_id=...`)
```json
{
  "bids": [{"price": "0.49", "size": "1000"}, {"price": "0.48", "size": "500"}],
  "asks": [{"price": "0.51", "size": "800"}, {"price": "0.52", "size": "1200"}]
}
```

### Midpoint (`/midpoint?token_id=...`)
```json
{"mid": "0.495"}
```

---

## Rate Limits & Best Practices

| Tier | Orders/min | Open Orders | Notes |
|------|------------|-------------|-------|
| Default ($0) | ~60 | ~100 | Check `/limits` for actual |
| Higher volume | Increases | Increases | Based on 30-day volume |

- **Use keyset pagination** (`after_cursor`) — never `offset`
- **Cache tag IDs** — resolve slug→ID once, reuse
- **Batch midpoint calls** — fetch multiple token IDs in parallel
- **Respect `orderMinSize`** — minimum order size per market (usually 5 USDC)
- **Respect `orderPriceMinTickSize`** — price precision (0.001 or 0.01)

---

## Environment Variables for Bot

```env
# Gamma (public)
GAMMA_API_BASE=https://gamma-api.polymarket.com

# CLOB (trading)
CLOB_API_BASE=https://clob.polymarket.com
POLY_API_KEY=...
POLY_API_SECRET=...
POLY_API_PASSPHRASE=...
POLY_PRIVATE_KEY=...          # For EOA signing (proxy creation)
POLY_FUNDER=...               # Funder address
RPC_URL=https://polygon-rpc.com
DRY_RUN=true
```

---

## OpenAPI Specs (for codegen)
- `https://docs.polymarket.com/api-spec/gamma-openapi.yaml`
- `https://docs.polymarket.com/api-spec/clob-openapi.yaml`
- `https://docs.polymarket.com/api-spec/data-openapi.yaml`
- `https://docs.polymarket.com/api-spec/bridge-openapi.yaml`

---

## Common Pitfalls (Learned from Building the Arb Bot)

1. **`clobTokenIds` is a JSON string** — must `json.loads()` to get array
2. **`outcomePrices` is a JSON string** — same, parse to array
3. **Gamma returns string numbers** — cast to `float`/`Decimal`
4. **Keyset pagination cursor** — pass as `after_cursor`, not `cursor`
5. **Tag filtering** — use numeric `tag_id` (resolve slug first via `/tags/slug/{slug}`)
6. **Binary market detection** — check `len(json.loads(clobTokenIds)) == 2` and `outcomes == ["Yes", "No"]`
7. **CLOB midpoint vs book** — midpoint is faster for scanning; book for depth analysis
8. **Rate limits** — Gamma is generous; CLOB authenticated endpoints stricter
9. **`enableOrderBook`** — must be `true` to trade via CLOB
10. **Fee schedule** — `rate` is in basis points (0.04 = 4 bps = 0.04%)

---

## Related Skills
- `hermes-agent` — for Hermes-specific patterns
- `polymarket-activity-pull` — for whale wallet tracking
- `web-browsing-log` — auto-logs API research to vault