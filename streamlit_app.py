import os
import streamlit as st
import pandas as pd
from io import BytesIO
import tempfile

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# --- pipeline imports ---
from src.text_extractor.pdf_extractor import extract_text_from_pdf
from src.text_extractor.image_extractor import is_ocr_available
from src.preprocessing.text_cleaner import clean_text
from src.extraction.email_extractor import extract_email
from src.extraction.phone_extractor import extract_phone
from src.extraction.name_extractor import extract_name_from_pdf


SUPPORTED_PDF_EXTENSIONS = {".pdf"}

NEON_GREEN = "39FF14"
BG_DARK = "0E1117"
CARD_DARK = "1B1F27"
LIGHT_TEXT = "E6E6E6"


def process_resume(file_path: str) -> dict:
    ext = os.path.splitext(file_path)[1].lower()

    if ext not in SUPPORTED_PDF_EXTENSIONS:
        return None

    raw_text = extract_text_from_pdf(file_path)
    name = extract_name_from_pdf(file_path)
    cleaned_text = clean_text(raw_text)

    return {
        "Name": name,
        "Email": extract_email(cleaned_text),
        "Phone": extract_phone(cleaned_text),
        "File": os.path.basename(file_path)
    }


def build_styled_excel(df: pd.DataFrame) -> BytesIO:
    """Write df to an in-memory xlsx and apply a neon-green / dark theme."""
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl", sheet_name="Resumes")
    buffer.seek(0)

    wb = load_workbook(buffer)
    ws = wb.active

    header_fill = PatternFill(start_color=NEON_GREEN, end_color=NEON_GREEN, fill_type="solid")
    header_font = Font(name="Calibri", size=12, bold=True, color=BG_DARK)
    header_align = Alignment(horizontal="center", vertical="center")

    body_font = Font(name="Calibri", size=11, color=BG_DARK)
    body_align = Alignment(horizontal="left", vertical="center")

    thin_border = Border(
        left=Side(style="thin", color=NEON_GREEN),
        right=Side(style="thin", color=NEON_GREEN),
        top=Side(style="thin", color=NEON_GREEN),
        bottom=Side(style="thin", color=NEON_GREEN),
    )

    # Header row
    for col_idx, col_name in enumerate(df.columns, start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_align
        cell.border = thin_border

    # Body rows — light fill, dark readable text, thin neon borders
    body_fill = PatternFill(start_color="F5FFF0", end_color="F5FFF0", fill_type="solid")
    for row_idx in range(2, ws.max_row + 1):
        for col_idx in range(1, ws.max_column + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = body_font
            cell.alignment = body_align
            cell.border = thin_border
            cell.fill = body_fill

    # Auto-size columns
    for col_idx, col_name in enumerate(df.columns, start=1):
        max_len = max(
            [len(str(col_name))] + [len(str(v)) for v in df.iloc[:, col_idx - 1].astype(str)]
        )
        ws.column_dimensions[get_column_letter(col_idx)].width = max_len + 6

    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 22

    out = BytesIO()
    wb.save(out)
    out.seek(0)
    return out


# ---------------- UI ----------------
st.set_page_config(page_title="Resume Parser", page_icon="🟢", layout="wide")

# ---------- THEME ----------
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            background-color: #{BG_DARK};
        }}

        /* ---- Header ---- */
        .app-header {{
            padding: 1.6rem 0 1rem 0;
            border-bottom: 1px solid #2A2F3A;
            margin-bottom: 1.5rem;
        }}
        .app-header h1 {{
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 2.4rem;
            color: #{LIGHT_TEXT};
            letter-spacing: 0.5px;
            margin-bottom: 0.2rem;
        }}
        .app-header h1 span {{
            color: #{NEON_GREEN};
            text-shadow: 0 0 12px rgba(57, 255, 20, 0.55);
        }}
        .app-header p {{
            font-family: 'Inter', sans-serif;
            color: #9AA0AC;
            font-size: 1rem;
            margin-top: 0;
        }}

        /* ---- Upload area ---- */
        section[data-testid="stFileUploaderDropzone"] {{
            background-color: #{CARD_DARK};
            border: 1.5px dashed #{NEON_GREEN}66;
            border-radius: 10px;
        }}
        section[data-testid="stFileUploaderDropzone"]:hover {{
            border: 1.5px dashed #{NEON_GREEN};
        }}

        /* ---- Dataframe ---- */
        div[data-testid="stDataFrame"] {{
            background-color: #{CARD_DARK};
            border: 1px solid #2A2F3A;
            border-radius: 8px;
            padding: 6px;
        }}
        thead tr th {{
            background-color: #23272F !important;
            color: #{LIGHT_TEXT} !important;
            font-family: 'Inter', sans-serif;
        }}

        /* ---- Section subheaders ---- */
        h2, h3 {{
            font-family: 'Poppins', sans-serif;
            color: #{LIGHT_TEXT} !important;
        }}

        /* ---- Download button ---- */
        .stDownloadButton button {{
            background-color: #{NEON_GREEN};
            color: #{BG_DARK};
            border-radius: 8px;
            border: none;
            padding: 0.7em 1.6em;
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            font-size: 0.95rem;
            box-shadow: 0 0 14px rgba(57, 255, 20, 0.45);
            transition: all 0.15s ease-in-out;
        }}
        .stDownloadButton button:hover {{
            background-color: #ffffff;
            color: #{BG_DARK};
            box-shadow: 0 0 22px rgba(57, 255, 20, 0.85);
            transform: translateY(-1px);
        }}

        /* ---- Progress bar ---- */
        div[data-testid="stProgress"] > div > div {{
            background-color: #{NEON_GREEN};
        }}

        /* ---- Alerts ---- */
        div[data-testid="stAlert"] {{
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="app-header">
        <h1>Resume <span>Parser</span></h1>
        <p>Upload PDF resumes and export clean, structured candidate data to Excel.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- ENVIRONMENT CHECK ----------
if not is_ocr_available():
    st.warning(
        "⚠️ OCR engine (Tesseract) not detected on this server. Scanned "
        "PDFs won't be read correctly — only text-based PDFs will work. "
        "If this app is deployed on Streamlit Cloud, add a `packages.txt` "
        "file to your repo root containing the line `tesseract-ocr` and redeploy."
    )

# ---------- SESSION STATE ----------
if "results" not in st.session_state:
    st.session_state.results = []

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

uploaded_files = st.file_uploader(
    "Upload resumes (PDF only)",
    type=["pdf"],
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
        failed_files = []

        with tempfile.TemporaryDirectory() as temp_dir:
            for i, file in enumerate(new_files, start=1):
                status.text(f"Processing: {file.name}")

                temp_path = os.path.join(temp_dir, file.name)
                with open(temp_path, "wb") as f:
                    f.write(file.read())

                result = process_resume(temp_path)
                if result:
                    st.session_state.results.append(result)
                else:
                    failed_files.append(file.name)

                st.session_state.processed_files.add(file.name)
                progress.progress(i / len(new_files))

        status.empty()
        progress.empty()

        if failed_files:
            st.error(f"❌ Could not process {len(failed_files)} file(s): {', '.join(failed_files)}")
        if len(new_files) - len(failed_files) > 0:
            st.success(f"✅ Successfully processed {len(new_files) - len(failed_files)} file(s)!")

# ---------- DISPLAY ----------
if st.session_state.results:
    df = pd.DataFrame(st.session_state.results)

    st.subheader("Extracted Data")
    st.dataframe(df, use_container_width=True)

    excel_buffer = build_styled_excel(df)

    st.download_button(
        label="⬇  Download Excel",
        data=excel_buffer,
        file_name="resume_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
