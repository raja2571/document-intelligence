def classify_document(text: str) -> str:
    """
    Classify a financial document based on extracted text.

    Returns:
        balance_sheet
        cash_flow
        invoices
        profit_and_loss
        unknown
    """

    if not text:
        return "unknown"

    text_lower = text.lower()

    # ============================================================
    # INVOICE
    # ============================================================

    invoice_keywords = [
        "invoice",
        "invoice number",
        "invoice no",
        "bill to",
        "ship to",
        "tax invoice",
        "subtotal",
        "total amount",
    ]

    # ============================================================
    # CASH FLOW
    # ============================================================

    cash_flow_keywords = [
        "cash flow",
        "cash flows from operating activities",
        "cash flows from investing activities",
        "cash flows from financing activities",
        "net increase in cash",
        "cash and cash equivalents",
    ]

    # ============================================================
    # BALANCE SHEET
    # ============================================================

    balance_sheet_keywords = [
        "balance sheet",
        "total assets",
        "total liabilities",
        "shareholders' equity",
        "shareholder equity",
        "current assets",
        "current liabilities",
    ]

    # ============================================================
    # PROFIT AND LOSS
    # ============================================================

    profit_loss_keywords = [
        "profit and loss",
        "profit & loss",
        "income statement",
        "statement of profit and loss",
        "revenue",
        "operating profit",
        "net profit",
        "net income",
    ]

    # ============================================================
    # CALCULATE SCORES
    # ============================================================

    scores = {
        "invoices": sum(
            keyword in text_lower
            for keyword in invoice_keywords
        ),

        "cash_flow": sum(
            keyword in text_lower
            for keyword in cash_flow_keywords
        ),

        "balance_sheet": sum(
            keyword in text_lower
            for keyword in balance_sheet_keywords
        ),

        "profit_and_loss": sum(
            keyword in text_lower
            for keyword in profit_loss_keywords
        ),
    }

    # ============================================================
    # FIND HIGHEST SCORE
    # ============================================================

    document_type = max(
        scores,
        key=scores.get,
    )

    # ============================================================
    # NO MATCH
    # ============================================================

    if scores[document_type] == 0:
        return "unknown"

    return document_type