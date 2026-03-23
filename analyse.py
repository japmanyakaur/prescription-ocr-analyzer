import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import json, io, re, os, sys

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyse(image_path):
    img = Image.open(image_path)
    buf = io.BytesIO()
    img.save(buf, format="PNG")

    model = genai.GenerativeModel("gemini-1.5-flash")

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
    return json.loads(raw)

def print_results(data):
    sep = "-" * 40

    print(f"\n{sep}")
    print(f"  Overall clarity: {int(data.get('overall_confidence', 0) * 100)}%")
    print(sep)

    meds = data.get("medicines", [])
    if meds:
        print("\nMEDICINES\n")
        for m in meds:
            print(f"  {m.get('name','—')}")
            print(f"  Dose: {m.get('dose','—')}  |  {m.get('frequency','—')}  |  {m.get('duration','—')}")
            print(f"  Purpose: {m.get('purpose','—')}")
            print(f"  Clarity: {int(m.get('confidence', 0.8) * 100)}%")
            print()

    summary = data.get("summary", "")
    if summary:
        print(f"SUMMARY\n\n  {summary}\n")

    si = data.get("special_instructions")
    if si and si != "null":
        print(f"INSTRUCTIONS\n\n  {si}\n")

    warns = data.get("warnings", [])
    if warns:
        print("WARNINGS\n")
        for w in warns:
            print(f"  ⚠  {w}")
        print()

    print(sep)
    print("  Always verify with your pharmacist before taking any medication.")
    print(sep + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyse.py <image_path>")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)

    print("Analysing prescription…")
    try:
        result = analyse(path)
        print_results(result)
    except json.JSONDecodeError:
        print("Error: couldn't parse response. Try a clearer image.")
    except Exception as e:
        print(f"Error: {e}")