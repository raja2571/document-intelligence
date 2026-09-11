import requests


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "http://127.0.0.1:8000"


# ============================================================
# EXPECTED RESULTS
# ============================================================

EXPECTED_RESULTS = {

    "Consolidated Balance Sheet 2017.pdf": {
        "document_id": "51b45f0f-cd36-46d2-91de-7d122a649f38",

        "expected": {
            "document_type": "balance_sheet",
            "year": 2017,
            "total_assets": 8923441607,
            "total_liabilities": 8923441607,
        }
    },

}


# ============================================================
# EVALUATE ONE DOCUMENT
# ============================================================

def evaluate_document(filename, document_info):

    document_id = document_info["document_id"]

    expected = document_info["expected"]

    print("\n" + "-" * 70)

    print("FILE:", filename)

    print("Document ID:", document_id)

    # --------------------------------------------------------
    # Get already processed document
    # --------------------------------------------------------

    try:

        response = requests.get(
            f"{BASE_URL}/api/v1/documents/{document_id}"
        )

    except Exception as e:

        print("ERROR:", e)

        return 0, len(expected)

    print(
        "HTTP Status:",
        response.status_code
    )

    # --------------------------------------------------------
    # Check API response
    # --------------------------------------------------------

    if response.status_code != 200:

        print("FAILED TO GET DOCUMENT")

        print(response.text)

        return 0, len(expected)

    result = response.json()

    # --------------------------------------------------------
    # Get extracted fields
    # --------------------------------------------------------

    actual = result.get(
        "extracted_fields",
        {}
    )

    print("\nActual Extracted Fields:")

    print(actual)

    # --------------------------------------------------------
    # Compare fields
    # --------------------------------------------------------

    passed = 0

    total = len(expected)

    print("\nField Evaluation:")

    print("-" * 70)

    for field, expected_value in expected.items():

        actual_value = actual.get(field)

        if actual_value == expected_value:

            print(
                f"PASS - {field}: "
                f"{actual_value}"
            )

            passed += 1

        else:

            print(
                f"FAIL - {field}"
            )

            print(
                f"       Expected: "
                f"{expected_value}"
            )

            print(
                f"       Actual  : "
                f"{actual_value}"
            )

    return passed, total


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)

    print(
        "FIELD-LEVEL ACCURACY EVALUATION"
    )

    print("=" * 70)

    print(
        "\nIMPORTANT:"
    )

    print(
        "This evaluation uses already processed documents."
    )

    print(
        "It does NOT upload PDFs or call Groq."
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    total_passed = 0

    total_fields = 0

    documents_passed = 0

    documents_failed = 0

    # --------------------------------------------------------
    # Evaluate documents
    # --------------------------------------------------------

    for filename, document_info in EXPECTED_RESULTS.items():

        passed, total = evaluate_document(
            filename,
            document_info
        )

        total_passed += passed

        total_fields += total

        if total > 0 and passed == total:

            documents_passed += 1

        else:

            documents_failed += 1

    # --------------------------------------------------------
    # Calculate accuracy
    # --------------------------------------------------------

    if total_fields > 0:

        accuracy = (
            total_passed
            / total_fields
        ) * 100

    else:

        accuracy = 0

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("\n" + "=" * 70)

    print(
        "FIELD ACCURACY SUMMARY"
    )

    print("=" * 70)

    print(
        "Total documents :",
        len(EXPECTED_RESULTS)
    )

    print(
        "Documents passed:",
        documents_passed
    )

    print(
        "Documents failed:",
        documents_failed
    )

    print(
        "Total fields    :",
        total_fields
    )

    print(
        "Correct fields  :",
        total_passed
    )

    print(
        "Incorrect fields:",
        total_fields - total_passed
    )

    print(
        f"Accuracy        : "
        f"{accuracy:.2f}%"
    )

    print("\n" + "=" * 70)

    if total_passed == total_fields:

        print(
            "ALL TESTED FIELDS PASSED"
        )

    else:

        print(
            "SOME FIELDS FAILED"
        )

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()