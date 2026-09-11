import requests


BASE_URL = "http://127.0.0.1:8000"


def evaluate_document(document_id, expected):
    """
    Fetch a processed document and compare
    extracted fields with expected values.
    """

    response = requests.get(
        f"{BASE_URL}/api/v1/documents/{document_id}"
    )

    print("\n" + "-" * 60)
    print("Document ID:", document_id)
    print("HTTP Status:", response.status_code)

    if response.status_code != 200:
        print("FAILED: Could not retrieve document")
        return False

    result = response.json()

    extracted = result.get("extracted_fields", {})

    print("Document Type:", extracted.get("document_type"))
    print("Year:", extracted.get("year"))
    print("Total Assets:", extracted.get("total_assets"))
    print("Total Liabilities:", extracted.get("total_liabilities"))
    print("Shareholders Equity:", extracted.get("shareholders_equity"))

    passed = True

    for field, expected_value in expected.items():

        actual_value = extracted.get(field)

        if actual_value == expected_value:
            print(f"PASS - {field}")
        else:
            print(
                f"FAIL - {field}: "
                f"expected={expected_value}, "
                f"actual={actual_value}"
            )
            passed = False

    return passed


if __name__ == "__main__":

    print("=" * 60)
    print("DOCUMENT INTELLIGENCE - EXTRACTION EVALUATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # Example evaluation
    # ---------------------------------------------------------

    document_id = "51b45f0f-cd36-46d2-91de-7d122a649f38"

    expected_values = {
        "document_type": "balance_sheet",
        "year": 2017,
        "total_assets": 8923441607,
        "total_liabilities": 8923441607,
    }

    result = evaluate_document(
        document_id,
        expected_values
    )

    print("\n" + "=" * 60)

    if result:
        print("EVALUATION PASSED")
    else:
        print("EVALUATION FAILED")

    print("=" * 60)