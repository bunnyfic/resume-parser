import os
import streamlit as st
import pandas as pd
from io import BytesIO
import tempfile

# --- pipeline imports ---
from src.text_extractor.pdf_extractor import extract_text_from_pdf
from src.text_extractor.image_extractor import extract_text_from_image, is_ocr_available
from src.preprocessing.text_cleaner import clean_text
from src.extraction.email_extractor import extract_email
from src.extraction.phone_extractor import extract_phone
from src.extraction.name_extractor import extract_name_from_pdf


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}


def process_resume(file_path: str) -> dict:
    ext = os.path.splitext(file_path)[1].lower()
    raw_text = ""
    name = None

    if ext in SUPPORTED_PDF_EXTENSIONS:
        raw_text = extract_text_from_pdf(file_path)
        name = extract_name_from_pdf(file_path)

    elif ext in SUPPORTED_IMAGE_EXTENSIONS:
        raw_text = extract_text_from_image(file_path)

    cleaned_text = clean_text(raw_text)

    return {
        "name": name,
        "email": extract_email(cleaned_text),
        "phone": extract_phone(cleaned_text),
        "file": os.path.basename(file_path)
    }


# ---------------- UI ----------------
st.set_page_config(page_title="Resume Parser", layout="wide")

# ---------- THEME ----------
# Base dark theme comes from .streamlit/config.toml (controls native widgets,
# sidebar, inputs, etc). This CSS only styles the pieces config.toml can't
# reach: the dataframe header row and the download button.
st.markdown(
    """
    <style>
        div[data-testid="stDataFrame"] {
            background-color: #1B1F27;
            border: 1px solid #2A2F3A;
            border-radius: 6px;
            padding: 6px;
        }
        thead tr th {
            background-color: #23272F !important;
            color: #E6E6E6 !important;
        }
        .stDownloadButton button {
            background-color: #7C9CFF;
            color: #0E1117;
            border-radius: 6px;
            border: none;
            padding: 0.6em 1.2em;
            font-weight: 600;
        }
        .stDownloadButton button:hover {
            background-color: #A0B6FF;
            color: #0E1117;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Resume Parser")
st.caption("Upload multiple resumes and export structured Excel output")

# ---------- ENVIRONMENT CHECK ----------
# Surfaces the #1 cause of "OCR works locally but not when deployed":
# the Tesseract binary itself isn't installed on the server.
if not is_ocr_available():
    st.warning(
        "⚠️ OCR engine (Tesseract) not detected on this server. Scanned "
        "PDFs and resumes with embedded images won't be read correctly — "
        "only plain-text PDFs will work. If this app is deployed on "
        "Streamlit Cloud, add a `packages.txt` file to your repo root "
        "containing the line `tesseract-ocr` and redeploy."
    )

# ---------- SESSION STATE ----------
if "results" not in st.session_state:
    st.session_state.results = []

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

uploaded_files = st.file_uploader(
    "Upload resumes (PDF, or JPG/PNG images)",
    type=["pdf", "jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# ---------- PROCESS FILES ----------
if uploaded_files:
    new_files = [
        f for f in uploaded_files
        if f.name not in st.session_state.processed_files
    ]

    if new_files:
        progress = st.progress(0)
        status = st.empty()

        with tempfile.TemporaryDirectory() as temp_dir:
            for i, file in enumerate(new_files, start=1):
                status.text(f"Processing: {file.name}")

                temp_path = os.path.join(temp_dir, file.name)
                with open(temp_path, "wb") as f:
                    f.write(file.read())

                st.session_state.results.append(process_resume(temp_path))
                st.session_state.processed_files.add(file.name)

                progress.progress(i / len(new_files))

        status.text("Processing completed.")
        progress.empty()

# ---------- DISPLAY ----------
if st.session_state.results:
    df = pd.DataFrame(st.session_state.results)

    st.subheader("Extracted Data")
    st.dataframe(df, use_container_width=True)

    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    st.download_button(
        label="Download Excel",
        data=excel_buffer,
        file_name="resume_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
