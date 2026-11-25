"""MCP server exposing ProPublica's Nonprofit Explorer API as tools.

API docs: https://projects.propublica.org/nonprofits/api
"""

from __future__ import annotations

import httpx
from mcp.server.mcpserver import MCPServer

BASE_URL = "https://projects.propublica.org/nonprofits/api/v2"
USER_AGENT = "nonprofit-explorer-mcp/0.1 (+https://github.com/ryanrickerts/nonprofit-explorer-mcp)"

mcp = MCPServer("nonprofit-explorer")


def _get(path: str, params: dict | None = None) -> dict:
    with httpx.Client(timeout=15.0, headers={"User-Agent": USER_AGENT}) as client:
        response = client.get(f"{BASE_URL}{path}", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def search_organizations(
    q: str | None = None,
    state: str | None = None,
    ntee: int | None = None,
    c_code: int | None = None,
    page: int = 0,
) -> dict:
    """Search ProPublica's Nonprofit Explorer for organizations.

    Matches against organization name, alternate name, and city. Results are
    paginated 25 at a time; use `page` to page through `num_pages`.

    Args:
        q: Keyword search string. Supports "exact phrases" in quotes, +required
            terms, and -excluded terms (e.g. `delta -dental`). Terms not
            prefixed with + or - are OR'd together.
        state: Two-letter USPS state/territory abbreviation (e.g. "WA"). Use
            "ZZ" for entities outside the US that file a US Form 990.
        ntee: National Taxonomy of Exempt Entities major group, 1-10
            (1=Arts/Culture/Humanities, 2=Education, 3=Environment/Animals,
            4=Health, 5=Human Services, 6=International/Foreign Affairs,
            7=Public/Societal Benefit, 8=Religion Related,
            9=Mutual/Membership Benefit, 10=Unknown/Unclassified).
        c_code: 501(c) subsection, e.g. 3 for 501(c)(3), 4 for 501(c)(4), or
            92 for section 4947(a)(1) trusts.
        page: Zero-indexed result page.
    """
    params: dict = {"page": page}
    if q:
        params["q"] = q
    if state:
        params["state[id]"] = state
    if ntee is not None:
        params["ntee[id]"] = ntee
    if c_code is not None:
        params["c_code[id]"] = c_code
    return _get("/search.json", params)


@mcp.tool()
def get_organization(ein: int) -> dict:
    """Look up a single nonprofit organization by EIN.

    Returns organization details plus its full filing history: for each tax
    year, extracted financial data where available (revenue, expenses,
    assets/liabilities, and compensation reported for officers/key employees),
    and links to the underlying 990/990-EZ/990-PF PDF and XML documents.

    Args:
        ein: The organization's 9-digit Employer Identification Number as an
            integer with no dashes (e.g. 911817868 for EIN 91-1817868).
    """
    return _get(f"/organizations/{ein}.json")


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
