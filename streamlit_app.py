import os
import streamlit as st
import pandas as pd
from io import BytesIO
import tempfile

# --- pipeline imports (UNCHANGED) ---
from src.text_extractor.pdf_extractor import extract_text_from_pdf
from src.text_extractor.image_extractor import extract_text_from_image
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
st.markdown(
    """
    <style>
        .stApp {
            background-color: #EBD2E9;
        }
        div[data-testid="stDataFrame"] {
            background-color: #ffffff;
            border-radius: 6px;
            padding: 6px;
        }
        thead tr th {
            background-color: #F2C9D6 !important;
            color: black !important;
        }
        .stDownloadButton button {
            background-color: #5E5E5E;
            color: white;
            border-radius: 0px;
            border: none;
            padding: 0.6em 1.2em;
            font-weight: 500;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Resume Parser")
st.caption("Upload multiple resumes and export structured Excel output")

# ---------- SESSION STATE ----------
if "results" not in st.session_state:
    st.session_state.results = []

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

uploaded_files = st.file_uploader(
    "Upload resumes (PDF or JPG-embedded PDFs only)",
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

    # ---------- EXCEL DOWNLOAD (NO REPROCESS BUG) ----------
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    st.download_button(
        label="Download Excel",
        data=excel_buffer,
        file_name="resume_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
