import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GROQ CONFIGURATION
# ============================================================

GROQ_API_KEY = os.getenv("LLM_API_KEY")

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "llama-3.3-70b-versatile",
)


if not GROQ_API_KEY:
    raise ValueError(
        "LLM_API_KEY is not configured in the .env file."
    )


client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# BALANCE SHEET FALLBACK
# ============================================================

def extract_total_liabilities_from_text(
    text: str,
):
    """
    Fallback extraction for total liabilities.

    Looks for the CAPITAL AND LIABILITIES section
    and extracts the first Total value from that section.
    """

    if not text:
        return None

    # --------------------------------------------------------
    # Find CAPITAL AND LIABILITIES section
    # --------------------------------------------------------

    match = re.search(
        r"CAPITAL\s+AND\s+LIABILITIES(.*?)(?=\bASSETS\b)",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return None

    liabilities_section = match.group(1)

    # --------------------------------------------------------
    # Find first Total in liabilities section
    # --------------------------------------------------------

    total_match = re.search(
        r"\bTotal\b\s+([\d,\s]+)",
        liabilities_section,
        re.IGNORECASE,
    )

    if not total_match:
        return None

    value = total_match.group(1)

    # Remove commas and spaces
    value = value.replace(",", "")
    value = value.replace(" ", "")

    try:
        return int(value)

    except ValueError:
        return None


# ============================================================
# EXTRACT FINANCIAL FIELDS
# ============================================================

def extract_financial_fields(
    text: str,
    document_type: str,
) -> dict[str, Any]:
    """
    Extract structured financial fields from a document
    using the Groq LLM.

    Supported document types:

        balance_sheet
        cash_flow
        invoices
        profit_and_loss
    """

    if not text:
        return {}

    if document_type == "unknown":
        return {}

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are a financial document information extraction system.

The document type is:

{document_type}

Extract the important structured fields from the document.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations.

GENERAL RULES:

1. If a field is not present, return null.
2. Do not invent values.
3. Preserve numerical values accurately.
4. Remove commas from numbers.
5. Return numbers as numbers, not strings.
6. Extract the year from the document if available.
7. Carefully distinguish values belonging to different years.
8. Use exactly the JSON structure requested below.


BALANCE SHEET RULES:

For a balance sheet:

- "total_liabilities" means the TOTAL amount under the
  CAPITAL AND LIABILITIES section.
- Do NOT use a value from the ASSETS section.
- The document may contain multiple "Total" values.
- Select the Total belonging to CAPITAL AND LIABILITIES.
- "total_assets" means the TOTAL amount under the ASSETS section.
- "shareholders_equity" should only be extracted when an
  explicit shareholders equity value is present.
- Do not calculate shareholders equity unless the document
  explicitly provides the required information.

Return:

{{
    "document_type": "balance_sheet",
    "year": null,
    "total_assets": null,
    "total_liabilities": null,
    "shareholders_equity": null
}}


CASH FLOW STATEMENT:

For a cash flow statement, return:

{{
    "document_type": "cash_flow",
    "year": null,
    "operating_cash_flow": null,
    "investing_cash_flow": null,
    "financing_cash_flow": null,
    "net_change_in_cash": null,
    "cash_and_cash_equivalents": null
}}


PROFIT AND LOSS STATEMENT:

For a profit and loss statement, return:

{{
    "document_type": "profit_and_loss",
    "year": null,
    "revenue": null,
    "operating_profit": null,
    "net_profit": null,
    "net_income": null
}}


INVOICE:

For an invoice, return:

{{
    "document_type": "invoices",
    "invoice_number": null,
    "invoice_date": null,
    "due_date": null,
    "vendor_name": null,
    "customer_name": null,
    "subtotal": null,
    "tax": null,
    "total_amount": null
}}


DOCUMENT TEXT:

--------------------
{text}
--------------------
"""

    # ========================================================
    # CALL GROQ
    # ========================================================

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You extract structured information "
                    "from financial documents. "
                    "Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
    )

    # ========================================================
    # GET LLM RESPONSE
    # ========================================================

    content = response.choices[0].message.content

    if not content:
        return {}

    content = content.strip()

    # ========================================================
    # REMOVE MARKDOWN JSON FENCES
    # ========================================================

    if content.startswith("```json"):
        content = content[7:]

    elif content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        extracted_fields = json.loads(
            content
        )

    except json.JSONDecodeError as e:

        raise ValueError(
            f"Groq returned invalid JSON: {e}"
        )

    # ========================================================
    # VALIDATE JSON OBJECT
    # ========================================================

    if not isinstance(
        extracted_fields,
        dict,
    ):
        raise ValueError(
            "Groq response is not a JSON object."
        )

    # ========================================================
    # FALLBACK FOR BALANCE SHEET
    # ========================================================

    if document_type == "balance_sheet":

        current_liabilities = extracted_fields.get(
            "total_liabilities"
        )

        # If Groq failed to extract total liabilities,
        # extract it directly from the document text.
        if current_liabilities is None:

            fallback_liabilities = (
                extract_total_liabilities_from_text(
                    text
                )
            )

            if fallback_liabilities is not None:

                extracted_fields[
                    "total_liabilities"
                ] = fallback_liabilities

    # ========================================================
    # RETURN RESULT
    # ========================================================

    return extracted_fields