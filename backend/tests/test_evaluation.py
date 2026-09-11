import requests
from pathlib import Path


BASE_URL = "http://127.0.0.1:8000"

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Final testing dataset
DATASET_FOLDER = PROJECT_ROOT / "dataset" / "final_test"


def test_all_documents():

    print("\n" + "=" * 70)
    print("FINAL DATASET EVALUATION")
    print("=" * 70)

    print("Dataset:", DATASET_FOLDER)

    pdf_files = list(DATASET_FOLDER.rglob("*.pdf"))

    print("PDF files found:", len(pdf_files))

    assert len(pdf_files) > 0, "No PDF files found"

    passed = 0
    failed = 0

    # ---------------------------------------------------------
    # Test every PDF
    # ---------------------------------------------------------

    for pdf_file in pdf_files:

        category = pdf_file.parent.name

        print("\n" + "-" * 70)
        print("File     :", pdf_file.name)
        print("Category :", category)

        try:

            # Upload document
            with open(pdf_file, "rb") as file:

                response = requests.post(
                    f"{BASE_URL}/api/v1/documents/upload",
                    files={
                        "file": (
                            pdf_file.name,
                            file,
                            "application/pdf"
                        )
                    }
                )

            print("HTTP Status:", response.status_code)

            if response.status_code != 200:

                print("FAILED")
                print(response.text)

                failed += 1
                continue

            result = response.json()

            extracted = result.get(
                "extracted_fields",
                {}
            )

            print(
                "Document Type:",
                extracted.get("document_type")
            )

            print(
                "Year:",
                extracted.get("year")
            )

            print(
                "Extracted Fields:",
                extracted
            )

            # -------------------------------------------------
            # Check document type
            # -------------------------------------------------

            expected_type = category

            actual_type = extracted.get(
                "document_type"
            )

            if actual_type == expected_type:

                print("PASS - document_type")
                passed += 1

            else:

                print(
                    "FAIL - document_type",
                    f"(expected={expected_type}, actual={actual_type})"
                )

                failed += 1

        except Exception as e:

            print("EXCEPTION:", e)
            failed += 1

    # ---------------------------------------------------------
    # Final summary
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL EVALUATION SUMMARY")
    print("=" * 70)

    print("Total PDFs :", len(pdf_files))
    print("Passed     :", passed)
    print("Failed     :", failed)

    if failed == 0:

        print("\nALL DOCUMENTS PASSED")

    else:

        print("\nSOME DOCUMENTS FAILED")


if __name__ == "__main__":

    test_all_documents()