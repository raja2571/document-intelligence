import requests


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "http://127.0.0.1:8000"


# ============================================================
# TEST 1: HEALTH CHECK
# ============================================================

def test_health():

    print("\n" + "=" * 60)
    print("TEST 1 - HEALTH CHECK")
    print("=" * 60)

    try:

        response = requests.get(
            f"{BASE_URL}/api/v1/health"
        )

        print("HTTP Status:", response.status_code)
        print("Response:", response.text)

        if response.status_code == 200:
            print("PASS - Health Check")
            return True

        print("FAIL - Health Check")
        return False

    except Exception as e:

        print("ERROR:", e)
        return False


# ============================================================
# TEST 2: GET ALL DOCUMENTS
# ============================================================

def test_get_all_documents():

    print("\n" + "=" * 60)
    print("TEST 2 - GET ALL DOCUMENTS")
    print("=" * 60)

    try:

        response = requests.get(
            f"{BASE_URL}/api/v1/documents/"
        )

        print("HTTP Status:", response.status_code)

        if response.status_code != 200:

            print("FAIL")
            print("Response:", response.text)

            return None

        documents = response.json()

        print(
            "Documents returned:",
            len(documents)
        )

        for document in documents:

            print("\n----------------------------------------")

            print(
                "Document ID:",
                document.get("document_id")
            )

            print(
                "Filename:",
                document.get("filename")
            )

            print(
                "Status:",
                document.get("status")
            )

            print(
                "Document Type:",
                document.get("document_type")
            )

        print("\nPASS - Get All Documents")

        return documents

    except Exception as e:

        print("ERROR:", e)

        return None


# ============================================================
# TEST 3: GET DOCUMENT BY ID
# ============================================================

def test_get_document_by_id(document_id):

    print("\n" + "=" * 60)
    print("TEST 3 - GET DOCUMENT BY ID")
    print("=" * 60)

    print(
        "Document ID:",
        document_id
    )

    try:

        response = requests.get(
            f"{BASE_URL}/api/v1/documents/{document_id}"
        )

        print(
            "HTTP Status:",
            response.status_code
        )

        if response.status_code != 200:

            print("FAIL")
            print("Response:", response.text)

            return False

        document = response.json()

        print(
            "Filename:",
            document.get("filename")
        )

        print(
            "Status:",
            document.get("status")
        )

        print(
            "Document Type:",
            document.get("document_type")
        )

        print(
            "Text Length:",
            document.get("text_length")
        )

        print(
            "Extracted Fields:",
            document.get("extracted_fields")
        )

        print("\nPASS - Get Document By ID")

        return True

    except Exception as e:

        print("ERROR:", e)

        return False


# ============================================================
# TEST 4: INVALID DOCUMENT ID
# ============================================================

def test_invalid_document_id():

    print("\n" + "=" * 60)
    print("TEST 4 - INVALID DOCUMENT ID")
    print("=" * 60)

    invalid_id = (
        "00000000-0000-0000-0000-000000000000"
    )

    print(
        "Testing ID:",
        invalid_id
    )

    try:

        response = requests.get(
            f"{BASE_URL}/api/v1/documents/{invalid_id}"
        )

        print(
            "HTTP Status:",
            response.status_code
        )

        print(
            "Response:",
            response.text
        )

        if response.status_code == 404:

            print("\nPASS - Invalid ID correctly returns 404")

            return True

        print("\nFAIL - Expected HTTP 404")

        return False

    except Exception as e:

        print("ERROR:", e)

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("DOCUMENT INTELLIGENCE API TEST")
    print("=" * 60)

    passed = 0
    failed = 0

    # --------------------------------------------------------
    # TEST 1
    # --------------------------------------------------------

    if test_health():

        passed += 1

    else:

        failed += 1

    # --------------------------------------------------------
    # TEST 2
    # --------------------------------------------------------

    documents = test_get_all_documents()

    if documents is not None:

        passed += 1

    else:

        failed += 1

    # --------------------------------------------------------
    # TEST 3
    # --------------------------------------------------------

    if documents and len(documents) > 0:

        first_document = documents[0]

        document_id = first_document.get(
            "document_id"
        )

        if document_id:

            if test_get_document_by_id(
                document_id
            ):

                passed += 1

            else:

                failed += 1

        else:

            print(
                "\nFAIL - Document ID not found"
            )

            failed += 1

    else:

        print(
            "\nSKIPPED - No stored documents available"
        )

    # --------------------------------------------------------
    # TEST 4
    # --------------------------------------------------------

    if test_invalid_document_id():

        passed += 1

    else:

        failed += 1

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL API TEST SUMMARY")
    print("=" * 60)

    print(
        "Tests passed:",
        passed
    )

    print(
        "Tests failed:",
        failed
    )

    print(
        "Total tests :",
        passed + failed
    )

    print("=" * 60)

    if failed == 0:

        print("ALL API TESTS PASSED")

    else:

        print("SOME API TESTS FAILED")

    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()