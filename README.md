# nonprofit-explorer-mcp

An MCP (Model Context Protocol) server that exposes [ProPublica's Nonprofit
Explorer API](https://projects.propublica.org/nonprofits/api) as tools, so an
MCP-aware assistant can search IRS Form 990 nonprofit tax filing data and pull
org-level financial/compensation detail directly, instead of being hand-fed
curl commands or screen-scraped pages.

This is an independent, unofficial project — not affiliated with or endorsed
by [ProPublica](https://github.com/propublica). It's a thin wrapper around
their public, unauthenticated API. See
[propublica/990-xml-reader](https://github.com/propublica/990-xml-reader)
(IRSx) for a complementary tool that parses bulk raw IRS XML 990 filings
rather than querying the hosted search API.

## Tools

- **`search_organizations`** — keyword search over org name/alt name/city,
  with optional filters for state, NTEE category, and 501(c) subsection.
  Wraps `GET /search.json`.
- **`get_organization`** — full detail for one org by EIN: filing history and
  extracted financials per tax year (revenue, expenses, assets, liabilities,
  and *aggregate* officer compensation), plus links to source PDF/XML
  filings. Wraps `GET /organizations/:ein.json`.

The underlying API only documents these two endpoints — no auth, no API key,
reasonable use expected (it's a public service, not built for bulk scraping).

## Installation

```bash
pip install -e .
```

Requires Python >= 3.10.

## Usage with Claude Code

```bash
claude mcp add nonprofit-explorer -- nonprofit-explorer-mcp
```

Or point at it directly in an MCP client config:

```json
{
  "mcpServers": {
    "nonprofit-explorer": {
      "command": "nonprofit-explorer-mcp"
    }
  }
}
```

## Example

> Search for "Pedal Project" in Washington state, then look up its EIN.

```
search_organizations(q="Pedal Project", state="WA")
-> {"ein": 911817868, "name": "Pedal Project", "city": "Bellingham", "state": "WA", ...}

get_organization(ein=911817868)
-> full filing history, financials, and officer compensation by year
```

## Known limitations

- **No per-person compensation.** `get_organization` returns only an
  aggregate officer/director compensation figure per tax year (e.g.
  `compnsatncurrofcr` for full Form 990 filers, `pct_compnsatncurrofcr` for
  990-EZ filers). It does not return the named officer/key-employee
  compensation table (Part IV of the 990-EZ, or Schedule J / Part VII of the
  full 990) — that breakdown is rendered by the ProPublica *website* from the
  underlying filing XML, but isn't in this API's JSON response. To get a named
  breakdown today you'd need to fetch and parse the filing's XML/PDF
  separately (e.g. with IRSx).
- **Regular employee wages are invisible.** For 990-EZ filers, total
  salary/wage expense appears only as a lump-sum line in Part I (not
  surfaced by this API at all — you'd have to read the source PDF/XML), with
  no per-employee detail. For full 990 filers, only officers/directors/key
  employees above the reporting threshold are itemized; rank-and-file pay
  isn't disclosed anywhere in the filing.
- **Extracted data lags the live site.** A newly filed return (e.g. filed
  mid-year) may show up on the ProPublica website before this API's
  `filings_with_data` array is backfilled with its extracted figures.
- **Filing/PDF downloads aren't included.** `pdf_url` values returned by the
  API are gated behind ProPublica's bot protection and can't be fetched with
  a plain HTTP client (they return an interstitial "Security Check" page
  instead of the PDF) — only the API's own JSON endpoints are reliably
  scriptable.
- **990-N ("e-Postcard") filers return no financial data at all.**
  Organizations with gross receipts under $50,000/year can file the minimal
  Form 990-N instead of a 990/990-EZ, which discloses no revenue, expense,
  asset, or compensation figures — just a confirmation that the org still
  qualifies. For these orgs, `get_organization` returns empty
  `filings_with_data` and `filings_without_data` arrays with no indication of
  *why* (as opposed to the org simply having no filings on record at all).
  The ProPublica website distinguishes this case ("Years with postcard
  filings (no financial data)"); this API does not.

## Development

```bash
pip install -e ".[dev]"
```

(No dev dependencies yet — add test tooling here as the project grows.)

## License

MIT
