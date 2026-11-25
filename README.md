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
- **`get_organization`** — full detail for one org by EIN: filing history,
  extracted financials per tax year (revenue, expenses, assets, liabilities),
  reported officer/key-employee compensation, and links to source PDF/XML
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

## Development

```bash
pip install -e ".[dev]"
```

(No dev dependencies yet — add test tooling here as the project grows.)

## License

MIT
