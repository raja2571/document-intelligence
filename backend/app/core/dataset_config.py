from pathlib import Path

DATASET_DIR = Path("dataset")

DOCUMENT_TYPES = {
    "balance_sheet": DATASET_DIR / "balance_sheet",
    "cash_flow": DATASET_DIR / "cash_flow",
    "invoice": DATASET_DIR / "invoices",
    "profit_and_loss": DATASET_DIR / "profit_and_loss",
}