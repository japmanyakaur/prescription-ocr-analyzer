# Prescription OCR Analyzer

AI-based system that extracts and interprets handwritten medical prescriptions using OCR and LLMs.  
Converts them into structured, readable, and user-friendly medical information.

---

##  Overview

Medical prescriptions are often difficult to read due to poor handwriting and use of abbreviations.  
This project addresses that problem by combining computer vision and AI reasoning to decode prescriptions and present them in a clear and structured format.

The system not only reads the prescription but also attempts to **understand the context**, including medicines, dosage, frequency, and instructions.

---

##  How It Works

1. **Image Input**  
   User uploads a prescription image via the interface  

2. **Text Extraction (OCR + Vision Model)**  
   The system processes the image using a vision-based AI model  

3. **Information Parsing**  
   Extracted text is structured into:
   - Medicines  
   - Dosage  
   - Instructions  

4. **AI Interpretation Layer**  
   A language model refines and organizes the data into meaningful output  

5. **Final Output**  
   Displays a clean, user-friendly summary with confidence levels  

---


##  Features

- Upload handwritten prescription images
- AI-powered text extraction (Gemini Vision)
- Medicine, dosage, frequency detection
- Structured and simplified output
- Confidence scoring and warnings

---

##  Tech Stack

- Python
- Streamlit
- Google Gemini API
- PIL

---

##  Setup

### 1. Clone repository
```bash
git clone <your-repo-link>
cd prescription-analyser
```
### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Add API key

Create a .env file:
```bash
GEMINI_API_KEY=your_api_key_here
```
### 3. Run application 
```bash
streamlit run app.py
```

## Disclaimer

This tool is for informational purposes only. Always consult a medical professional before taking any medication.


---


