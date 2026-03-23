import streamlit as st
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import json, io, re, os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="Prescription Analyser", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #111 !important;
    color: #e0e0e0 !important;
    font-family: 'Inter', sans-serif !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none; }
.block-container { max-width: 680px !important; padding: 3rem 1.5rem !important; }

h1 { font-size: 1.1rem !important; font-weight: 600 !important; color: #fff !important; margin-bottom: 0.2rem !important; }
p.sub { font-size: 0.8rem; color: #666; margin-bottom: 2rem; }

input, textarea {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #e0e0e0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
}

[data-testid="stFileUploader"] {
    background: #1a1a1a !important;
    border: 1px dashed #2d2d2d !important;
    border-radius: 10px !important;
}

div.stButton > button {
    background: #fff !important;
    color: #111 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.55rem 1.4rem !important;
    width: 100% !important;
}
div.stButton > button:hover { background: #e8e8e8 !important; }

.block {
    background: #161616;
    border: 1px solid #222;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.block-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #555;
    margin-bottom: 0.7rem;
}
.med-row {
    padding: 0.7rem 0;
    border-bottom: 1px solid #1e1e1e;
    font-size: 0.88rem;
}
.med-row:last-child { border-bottom: none; padding-bottom: 0; }
.med-name { color: #fff; font-weight: 500; margin-bottom: 0.25rem; }
.med-purpose { color: #888; font-size: 0.8rem; margin-top: 0.2rem; font-style: italic; }
.pill {
    display: inline-block;
    background: #1e1e1e;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    padding: 0.1rem 0.5rem;
    font-size: 0.75rem;
    color: #aaa;
    margin-right: 0.4rem;
}
.warn { color: #c87941; font-size: 0.83rem; padding: 0.5rem 0; border-bottom: 1px solid #1e1e1e; }
.warn:last-child { border-bottom: none; padding-bottom: 0; }
.plain { font-size: 0.88rem; color: #aaa; line-height: 1.7; }
.conf { font-size: 0.78rem; color: #555; margin-top: 0.4rem; }
.note { font-size: 0.75rem; color: #444; margin-top: 2rem; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Prescription Analyser</h1>", unsafe_allow_html=True)
st.markdown('<p class="sub">Upload a photo of any prescription to decode it.</p>', unsafe_allow_html=True)

uploaded = st.file_uploader("Upload prescription", type=["jpg","jpeg","png","webp","bmp"], label_visibility="collapsed")

if uploaded:
    img = Image.open(uploaded)
    st.image(img, use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Analyse"):
        with st.spinner("Reading prescription…"):
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")

                buf = io.BytesIO()
                img.save(buf, format="PNG")

                prompt = """Analyse this prescription. Return ONLY valid JSON, no markdown.

{
  "medicines": [
    {
      "name": "medicine name",
      "dose": "e.g. 500mg",
      "frequency": "e.g. Twice daily",
      "duration": "e.g. 5 days",
      "purpose": "one sentence on what this treats",
      "confidence": 0.9
    }
  ],
  "summary": "2-3 sentences in plain language",
  "warnings": ["any warnings or empty array"],
  "special_instructions": "any notes or null",
  "overall_confidence": 0.88
}

Use Unknown for unreadable fields. confidence = how clearly you read it (0-1)."""

                resp = model.generate_content([prompt, {"mime_type": "image/png", "data": buf.getvalue()}])
                raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", resp.text.strip())
                data = json.loads(raw)

                meds = data.get("medicines", [])
                if meds:
                    rows = ""
                    for m in meds:
                        conf = int(m.get("confidence", 0.8) * 100)
                        rows += f"""<div class="med-row">
                            <div class="med-name">{m.get('name','—')}</div>
                            <div>
                                <span class="pill">{m.get('dose','—')}</span>
                                <span class="pill">{m.get('frequency','—')}</span>
                                <span class="pill">{m.get('duration','—')}</span>
                            </div>
                            <div class="med-purpose">{m.get('purpose','')}</div>
                            <div class="conf">Clarity {conf}%</div>
                        </div>"""
                    st.markdown(f'<div class="block"><div class="block-label">Medicines</div>{rows}</div>', unsafe_allow_html=True)

                summary = data.get("summary", "")
                if summary:
                    st.markdown(f'<div class="block"><div class="block-label">Summary</div><p class="plain">{summary}</p></div>', unsafe_allow_html=True)

                si = data.get("special_instructions")
                if si and si != "null":
                    st.markdown(f'<div class="block"><div class="block-label">Instructions</div><p class="plain">{si}</p></div>', unsafe_allow_html=True)

                warns = data.get("warnings", [])
                if warns:
                    warn_html = "".join(f'<div class="warn">⚠ {w}</div>' for w in warns)
                    st.markdown(f'<div class="block"><div class="block-label">Warnings</div>{warn_html}</div>', unsafe_allow_html=True)

                st.markdown('<p class="note">Always verify with your pharmacist before taking any medication. This tool is for reference only.</p>', unsafe_allow_html=True)

            except json.JSONDecodeError:
                st.error("Couldn't parse the response. Try a clearer image.")
            except Exception as e:
                st.error(f"Error: {e}")