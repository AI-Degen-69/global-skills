---
name: data-source-indicator
description: Use when you need to surface whether displayed data came from a live API or a fallback/local source
---

## Pattern

A small inline UI element answering: *where did this data come from, and when?*

### Structure

```
<dot> Via: <MODE> at HH:MM
```

- **Dot color**: green = live API, gray = fallback/estimation
- **Mode**: short label (e.g. `IBKR`, `Finnhub`, `Seed`, `Cached`)
- **Timestamp**: `HH:MM` formatted from source's timestamp; fall back to `new Date()` if unavailable

### Props

| Name | Type | Example |
|------|------|---------|
| `mode` | `'ibkr' \| 'seed' \| 'api' \| 'cached'` | determines dot color and label text |
| `timestamp` | string (HH:MM) | formatted hour:minute |

### Color mapping (handle with care — no magic globals)

```ts
const dotColor = mode === 'ibkr' ? '#22c55e' : '#6b7280';
```

Extend as needed per domain.

### Timestamp sourcing

Priority:
1. Snapshot's authoritative field (e.g. `portfolio.syncedAt`, `data.fetchedAt`)
2. localStorage key (client-side hydration metadata)
3. `new Date()` (wall-clock, last resort)

```ts
const time = snapshot?.syncedAt
  ?? localStorage.getItem('APP_DATA_TIMESTAMP_KEY')
  ?? Date.now();

const formatted = new Date(time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
// or manual: `${d.getHours().toString().padStart(2,'0')}:${...}`
```

### Integration with portfolio / cache layers

When using React Query or similar:

```ts
const { data: portfolio, isFetched, isError } = useLivePortfolio();

const sourceMode = isFetched && portfolio && !isError ? 'live' : 'fallback';
const timestamp  = portfolio?.syncedAt ?? Date.now();
```

### Styling

Inline styles recommended (no external dependency). Match surrounding font stack. Monospace for timestamp.
