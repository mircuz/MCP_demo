"""
Vita Insurance API tools — life insurance policy management.

These tools call the customer's REST API for "Polizze Vita" (life insurance).
See swagger_API_Vita.txt for the full OpenAPI 2.0 specification.

TO ACTIVATE:
  1. Set real values in config.py for VITA_API_BASE_URL, VITA_API_TOKEN,
     and VITA_DEFAULT_COMPAGNIA.
  2. Restart the MCP server.
"""

from __future__ import annotations

import json
import urllib.request
from config import VITA_API_BASE_URL, VITA_API_TOKEN, VITA_DEFAULT_COMPAGNIA


def _vita_get(path: str, params: dict | None = None) -> dict:
    """Make an authenticated GET request to the Vita API.

    Args:
        path:   Path appended to VITA_API_BASE_URL (e.g. "/UNIPOL/portafoglio/vita/v1/polizze").
        params: Optional query-string parameters.

    Returns:
        Parsed JSON response as a dict.

    Raises:
        RuntimeError: If the API returns a non-200 status or the placeholder
                      config has not been replaced.
    """
    if "PLACEHOLDER" in VITA_API_BASE_URL or "PLACEHOLDER" in VITA_API_TOKEN:
        raise RuntimeError(
            "Vita API not configured. Update VITA_API_BASE_URL and "
            "VITA_API_TOKEN in config.py with real values."
        )

    url = f"{VITA_API_BASE_URL}{path}"

    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if qs:
            url = f"{url}?{qs}"

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {VITA_API_TOKEN}")
    req.add_header("X-UNIPOL-REQUESTID", "mcp-demo-request")
    req.add_header("Accept", "application/json")

    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


# ─────────────────────────────────────────────────────────────────────────────
#  Registration
# ─────────────────────────────────────────────────────────────────────────────

def register(mcp, w):
    """Register Vita insurance API tools with the MCP server."""

    # ── Polizze (Policies) ───────────────────────────────────────────────

    @mcp.tool()
    def vita_list_polizze(
        id_soggetto: str,
        compagnia: str = VITA_DEFAULT_COMPAGNIA,
        agenzia: str | None = None,
        flag_vigore: str = "S",
        page: int = 0,
        per_page: int = 15,
    ) -> str:
        """List life-insurance policies for a given subject (codice fiscale / partyId).

        Args:
            id_soggetto: Fiscal code or partyId of the policyholder (required).
            compagnia:   Insurance company code (path param).
            agenzia:     Optional agency filter.
            flag_vigore: 'S' for active policies only (default), 'N' for all.
            page:        Page number (0-based).
            per_page:    Results per page (default 15).
        """
        path = f"/{compagnia}/portafoglio/vita/v1/polizze"
        params = {
            "idSoggetto": id_soggetto,
            "agenzia": agenzia,
            "flagVigore": flag_vigore,
            "page": str(page),
            "per_page": str(per_page),
        }
        try:
            data = _vita_get(path, params)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    @mcp.tool()
    def vita_get_polizza(
        polizza_id: str,
        compagnia: str = VITA_DEFAULT_COMPAGNIA,
    ) -> str:
        """Get full details of a specific life-insurance policy.

        Args:
            polizza_id: The policy identifier.
            compagnia:  Insurance company code.
        """
        path = f"/{compagnia}/portafoglio/vita/v1/polizze/{polizza_id}"
        try:
            data = _vita_get(path)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    @mcp.tool()
    def vita_get_beneficiari(
        polizza_id: str,
        compagnia: str = VITA_DEFAULT_COMPAGNIA,
    ) -> str:
        """Get the list of beneficiaries for a life-insurance policy.

        Args:
            polizza_id: The policy identifier.
            compagnia:  Insurance company code.
        """
        path = f"/{compagnia}/portafoglio/vita/v1/polizze/{polizza_id}/beneficiari"
        try:
            data = _vita_get(path)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    @mcp.tool()
    def vita_get_dettaglio_pagamenti(
        polizza_id: str,
        compagnia: str = VITA_DEFAULT_COMPAGNIA,
    ) -> str:
        """Get payment details for a life-insurance policy.

        Args:
            polizza_id: The policy identifier.
            compagnia:  Insurance company code.
        """
        path = f"/{compagnia}/portafoglio/vita/v1/polizze/{polizza_id}/dettaglioPagamenti"
        try:
            data = _vita_get(path)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    @mcp.tool()
    def vita_get_premi_base(
        polizza_id: str,
        compagnia: str = VITA_DEFAULT_COMPAGNIA,
    ) -> str:
        """Get base premiums (weekly/monthly) for a life-insurance policy.

        Args:
            polizza_id: The policy identifier.
            compagnia:  Insurance company code.
        """
        path = f"/{compagnia}/portafoglio/vita/v1/polizze/{polizza_id}/premi/base"
        try:
            data = _vita_get(path)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    @mcp.tool()
    def vita_get_premi_fondi(
        polizza_id: str,
        compagnia: str = VITA_DEFAULT_COMPAGNIA,
    ) -> str:
        """Get fund premiums for a life-insurance policy.

        Args:
            polizza_id: The policy identifier.
            compagnia:  Insurance company code.
        """
        path = f"/{compagnia}/portafoglio/vita/v1/polizze/{polizza_id}/premi/fondi"
        try:
            data = _vita_get(path)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    @mcp.tool()
    def vita_get_premi_multiramo(
        polizza_id: str,
        compagnia: str = VITA_DEFAULT_COMPAGNIA,
    ) -> str:
        """Get multi-branch premiums for a life-insurance policy.

        Args:
            polizza_id: The policy identifier.
            compagnia:  Insurance company code.
        """
        path = f"/{compagnia}/portafoglio/vita/v1/polizze/{polizza_id}/premi/multiramo"
        try:
            data = _vita_get(path)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    @mcp.tool()
    def vita_get_premi_pip(
        polizza_id: str,
        compagnia: str = VITA_DEFAULT_COMPAGNIA,
    ) -> str:
        """Get PIP (individual pension plan) premiums for a life-insurance policy.

        Args:
            polizza_id: The policy identifier.
            compagnia:  Insurance company code.
        """
        path = f"/{compagnia}/portafoglio/vita/v1/polizze/{polizza_id}/premi/pip"
        try:
            data = _vita_get(path)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    @mcp.tool()
    def vita_get_ruoli_polizza(
        polizza_id: str,
        compagnia: str = VITA_DEFAULT_COMPAGNIA,
    ) -> str:
        """Get the roles (subjects) associated with a life-insurance policy.

        Args:
            polizza_id: The policy identifier.
            compagnia:  Insurance company code.
        """
        path = f"/{compagnia}/portafoglio/vita/v1/polizze/{polizza_id}/ruoli"
        try:
            data = _vita_get(path)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    # ── Proposte (Proposals) ─────────────────────────────────────────────

    @mcp.tool()
    def vita_list_proposte(
        id_soggetto: str,
        compagnia: str = VITA_DEFAULT_COMPAGNIA,
        agenzia: str | None = None,
        flag_vigore: str = "S",
        page: int = 0,
        per_page: int = 15,
    ) -> str:
        """List life-insurance proposals for a given subject.

        Args:
            id_soggetto: Fiscal code or partyId of the proposer (required).
            compagnia:   Insurance company code.
            agenzia:     Optional agency filter.
            flag_vigore: 'S' for active proposals only (default), 'N' for all.
            page:        Page number (0-based).
            per_page:    Results per page (default 15).
        """
        path = f"/{compagnia}/portafoglio/vita/v1/proposte"
        params = {
            "idSoggetto": id_soggetto,
            "agenzia": agenzia,
            "flagVigore": flag_vigore,
            "page": str(page),
            "per_page": str(per_page),
        }
        try:
            data = _vita_get(path, params)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    @mcp.tool()
    def vita_get_proposta(
        proposta_id: str,
        compagnia: str = VITA_DEFAULT_COMPAGNIA,
    ) -> str:
        """Get full details of a specific life-insurance proposal.

        Args:
            proposta_id: The proposal identifier.
            compagnia:   Insurance company code.
        """
        path = f"/{compagnia}/portafoglio/vita/v1/proposte/{proposta_id}"
        try:
            data = _vita_get(path)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    @mcp.tool()
    def vita_get_ruoli_proposta(
        proposta_id: str,
        compagnia: str = VITA_DEFAULT_COMPAGNIA,
    ) -> str:
        """Get the roles (subjects) associated with a life-insurance proposal.

        Args:
            proposta_id: The proposal identifier.
            compagnia:   Insurance company code.
        """
        path = f"/{compagnia}/portafoglio/vita/v1/proposte/{proposta_id}/ruoli"
        try:
            data = _vita_get(path)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)})
