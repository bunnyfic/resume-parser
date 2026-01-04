# resume-parser
# Resume Parser & Candidate Data Extractor

A Python-based resume parsing application that automatically extracts **Name, Email, and Phone Number** from multiple resumes and exports the results into a structured Excel sheet.

Built to reduce repetitive manual screening work for recruiters and HR teams.

---

## Features

- Upload **multiple resumes at once**
- Supports **PDF resumes**, including **image-based (scanned) PDFs**
- Automatically extracts:
  - Candidate Name
  - Email Address
  - Phone Number
- Outputs clean, structured data in **Excel format**
- Interactive **Streamlit web interface**
- Modular, extensible backend architecture

---

## Tech Stack

- **Python**
- **Streamlit** – Web UI
- **pdfplumber** – PDF text & layout extraction
- **pytesseract** – OCR for image-based PDFs
- **spaCy** – NLP-assisted name detection
- **Pandas** – Data handling & Excel export
- **OpenPyXL** – Excel file generation

---

## Project Structure

# Resume Parser & Candidate Data Extractor

A Python-based resume parsing application that automatically extracts **Name, Email, and Phone Number** from multiple resumes and exports the results into a structured Excel sheet.

Built to reduce repetitive manual screening work for recruiters and HR teams.

---

## Features

- Upload **multiple resumes at once**
- Supports **PDF resumes**, including **image-based (scanned) PDFs**
- Automatically extracts:
  - Candidate Name
  - Email Address
  - Phone Number
- Outputs clean, structured data in **Excel format**
- Interactive **Streamlit web interface**
- Modular, extensible backend architecture

---

## Tech Stack

- **Python**
- **Streamlit** – Web UI
- **pdfplumber** – PDF text & layout extraction
- **pytesseract** – OCR for image-based PDFs
- **spaCy** – NLP-assisted name detection
- **Pandas** – Data handling & Excel export
- **OpenPyXL** – Excel file generation

---

## Project Structure
resume-parser/
│
├── streamlit_app.py # Streamlit frontend
├── requirements.txt # Dependencies
├── README.md
│
├── src/
│ ├── text_extractor/
│ │ ├── pdf_extractor.py
│ │ └── image_extractor.py
│ │
│ ├── preprocessing/
│ │ └── text_cleaner.py
│ │
│ ├── extraction/
│ │ ├── name_extractor.py
│ │ ├── email_extractor.py
│ │ └── phone_extractor.py
│ │
│ └── pipeline/
│ └── resume_pipeline.py
│
└── data/
├── raw/ # Input resumes
└── output/ # Generated Excel files


---

## How It Works

1. User uploads one or more resume PDFs
2. The system:
   - Extracts text using layout parsing and OCR (if needed)
   - Cleans noisy OCR text
   - Detects name using hybrid NLP + rule-based logic
   - Extracts email and phone using robust regex handling
3. All results are compiled into a single table
4. User downloads the final Excel file

---

## Running Locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
