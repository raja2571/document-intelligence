# 📄 Document Intelligence API

An AI-powered FastAPI application that processes financial PDF documents, extracts text, identifies document types, and extracts structured financial information using a Groq-hosted LLM.

The system supports Balance Sheets, Cash Flow Statements, Profit & Loss Statements, and Invoices, with database storage and REST API endpoints for retrieving processed documents.

---

## 🚀 Features

### 📤 Document Upload

- Upload PDF documents through a REST API
- File validation before processing
- Unique document ID generated for every upload
- Uploaded documents stored locally

### 📑 Text Extraction

- Extracts readable text from PDF documents
- Stores extracted text with document metadata
- Tracks extracted text length

### 🤖 Document Classification

Automatically identifies supported document types:

- Balance Sheet
- Cash Flow Statement
- Profit & Loss Statement
- Invoice

### 🔍 Financial Field Extraction

Uses a Groq-hosted LLM to extract structured information.

**Balance Sheet**

- Year
- Total Assets
- Total Liabilities
- Shareholders' Equity

**Cash Flow Statement**

- Year
- Operating Cash Flow
- Investing Cash Flow
- Financing Cash Flow
- Net Change in Cash
- Cash and Cash Equivalents

**Profit & Loss Statement**

- Year
- Revenue
- Operating Profit
- Net Profit
- Net Income

**Invoice**

- Invoice Number
- Invoice Date
- Due Date
- Vendor Name
- Customer Name
- Subtotal
- Tax
- Total Amount

### 💾 Database Storage

Processed documents and extracted information are stored in a database.

Stored information includes:

- Document ID
- Filename
- File path
- Processing status
- Document type
- Extracted text
- Extracted fields
- Creation timestamp

### 🔌 REST API

The application provides endpoints for:

- Uploading documents
- Retrieving a document
- Retrieving all documents
- Checking API health

### 🧪 Testing

The project includes API and field-level evaluation tests.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Programming Language | Python |
| API Framework | FastAPI |
| LLM | Groq API |
| LLM Model | Configured through `.env` |
| Database | SQLite |
| ORM | SQLAlchemy |
| Data Validation | Pydantic |
| PDF Processing | PDF text extraction |
| Environment Configuration | python-dotenv |
| API Testing | Requests |
| API Documentation | Swagger / OpenAPI |

---

## 🏗️ Architecture

```text
                    PDF Document
                         │
                         ▼
                ┌─────────────────┐
                │  FastAPI API    │
                │  Document Upload│
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ File Validation │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ PDF Text        │
                │ Extraction      │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Document        │
                │ Classification  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Groq LLM        │
                │ Field Extraction│
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Structured JSON │
                │ Result          │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Database        │
                │ Storage         │
                └────────┬────────┘
                         │
                         ▼
                  REST API Response
```

---

## 📁 Project Structure

```text
document-intelligence/
│
├── backend/
│   ├── app/
│   │   ├── ...
│   │   └── main.py
│   │
│   └── tests/
│       ├── test_api.py
│       ├── test_field_accuracy.py
│       └── ...
│
├── dataset/
│   ├── balance_sheet/
│   ├── cash_flow/
│   ├── profit_and_loss/
│   ├── invoices/
│   └── final_test/
│
├── uploads/
│
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

> The exact files inside `backend/app` may vary depending on the final project structure.

---

## ⚙️ Prerequisites

Before running the project, install:

- Python 3.10+
- Git
- A Groq API key

---

## 🔧 Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd document-intelligence
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

Example:

```env
LLM_API_KEY=your_groq_api_key_here
LLM_MODEL=your_configured_model
```

**Never commit the real `.env` file to GitHub.**

---

## ▶️ Running the Application

Start the FastAPI server:

```powershell
uvicorn backend.app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## 📚 API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
```

---

## 🔌 API Endpoints

### Health Check

```http
GET /api/v1/health
```

Example response:

```json
{
  "status": "healthy",
  "message": "Document Intelligence API is running"
}
```

---

### Upload Document

```http
POST /api/v1/documents/upload
```

Request:

```text
multipart/form-data
file = document.pdf
```

Example response:

```json
{
  "document_id": "unique-document-id",
  "filename": "Consolidated Balance Sheet 2017.pdf",
  "status": "processed",
  "document_type": "balance_sheet",
  "size_bytes": 123456,
  "text_length": 1698,
  "extracted_fields": {
    "document_type": "balance_sheet",
    "year": 2017,
    "total_assets": 8923441607,
    "total_liabilities": 8923441607,
    "shareholders_equity": null
  }
}
```

---

### Get Document

```http
GET /api/v1/documents/{document_id}
```

Returns the stored document information and extracted fields.

---

### Get All Documents

```http
GET /api/v1/documents/
```

Returns all documents stored in the database.

---

## 🧪 Testing

The project contains API testing and field-level evaluation scripts.

### API Tests

Run:

```powershell
python backend\tests\test_api.py
```

The API test verifies:

- Health check
- Get all documents
- Get document by ID
- Invalid document ID handling

### Field Accuracy Evaluation

Run:

```powershell
python backend\tests\test_field_accuracy.py
```

This compares extracted fields against expected values from the final test dataset.

> Repeated field-accuracy tests may consume LLM API tokens because document uploads trigger LLM extraction.

---

## 📊 Evaluation

A successfully stored Balance Sheet document was evaluated using four fields:

```text
document_type
year
total_assets
total_liabilities
```

Evaluation result:

```text
Total fields    : 4
Correct fields  : 4
Incorrect fields: 0
Accuracy        : 100.00%
```

The six-document evaluation was also implemented. However, repeated LLM calls were affected by the Groq token-per-day rate limit.

Therefore, the 100% result above represents the successfully evaluated document and should not be interpreted as a 100% accuracy claim for the complete dataset.

---

## ⚠️ Error Handling

The API handles common failures including:

- Invalid document ID
- Missing document
- Unsupported file
- Empty file
- LLM extraction failure
- LLM rate-limit errors
- Invalid LLM JSON responses

For example, when the LLM provider reaches its token limit, the API returns a clear rate-limit error rather than silently producing incorrect extraction results.

---

## 🔐 Security

- API keys are loaded from environment variables.
- API keys are not hardcoded in Python source code.
- `.env` is excluded using `.gitignore`.
- Uploaded/generated local files can be excluded from Git.
- Never commit credentials or API keys to GitHub.

---

## ⚠️ Known Limitations

- LLM extraction depends on the quality of extracted PDF text.
- LLM calls are affected by provider rate limits.
- Scanned/image-only PDFs may require OCR for reliable extraction.
- Extraction accuracy can vary depending on document layout.
- Repeated evaluation uploads consume LLM tokens.

---

## 🔮 Future Improvements

Possible improvements include:

- OCR support for scanned PDFs
- Asynchronous document processing
- LLM response caching
- Automatic retry and exponential backoff
- Stronger structured-output validation
- Deterministic extraction fallbacks
- Authentication and authorization
- Improved logging and monitoring
- Pagination and filtering for document retrieval
- Cloud storage for uploaded documents
- Larger benchmark datasets for accuracy evaluation

---

## 📌 Example Workflow

```text
1. Start FastAPI server
        ↓
2. Open Swagger UI
        ↓
3. Upload financial PDF
        ↓
4. Extract PDF text
        ↓
5. Identify document type
        ↓
6. Extract structured fields
        ↓
7. Store result in database
        ↓
8. Return JSON response
        ↓
9. Retrieve document using document ID
```

---

## 👨‍💻 Project Highlights

This project demonstrates practical experience with:

- REST API development
- FastAPI
- Python
- LLM integration
- Financial document processing
- PDF text extraction
- Structured information extraction
- Database persistence
- API validation
- Error handling
- Automated testing
- Git and GitHub

---

## 📄 Project Report

A detailed project report is included separately, covering:

- Project overview
- Objectives
- Architecture
- Document processing workflow
- Technologies used
- API endpoints
- Database
- LLM integration
- Testing
- Evaluation
- Limitations
- Future improvements

---

## 📜 License

This project was developed as an internship/academic project.# Document Intelligence API

A FastAPI-based document intelligence system that uploads financial documents,
extracts text, identifies the document type, extracts structured fields using
an LLM, and stores the processed information in a database.
