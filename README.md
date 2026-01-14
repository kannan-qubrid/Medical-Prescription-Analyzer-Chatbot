# Medical Prescription Analyzer Chatbot 💊

A production-grade, structured medical intelligence platform powered by **Qubrid AI**, **LangChain**, and **Streamlit**. This assistant specializes in analyzing medical prescriptions (handwritten or digital) through a multi-step vision reasoning pipeline, extracting structured data, and providing focused medical insights.

---

## 🚀 Key Features

### 🔍 4-Step Medical Reasoning Pipeline
The core of the application is a robust backend pipeline that processes prescription images:
1.  **Vision OCR Extraction**: Transcribes text from the image, focusing on medicine names and dosages.
2.  **Entity Normalization**: Converts raw text into a structured JSON schema.
3.  **Ambiguity Audit**: Identifies low-confidence extractions or missing information.
4.  **Safety Audit**: Performs a safety check on extracted instructions and conflicting timings.

### 📅 Smart Prescription Schedule (NEW)
A specialized, safety-first workflow to convert prescriptions into daily timelines:
-   **Readiness Gate**: Automatically flags missing critical info (Dosage, Frequency, Duration).
-   **Guided Clarification**: Interactive form-based UI to fill data gaps before generation.
-   **Visual Timeline**: Tabular daily schedule with Morning/Afternoon/Night slots.
-   **PDF Export**: Downloadable medication schedule with mandatory patient disclaimers.

### 💬 Focused Medical Chat Modes
Users can interact with the analyzed prescription using specialized modes:
-   **🩺 Explain Prescription**: General explanation of purpose and usage.
-   **⚠️ Safety Check**: Highlights precautions, side effects, and contraindications.
-   **📄 Summary for Caregiver**: Produce concise bullet-point summaries.

### 💾 Persistent Intelligence (SQLite)
-   **Conversation Restore**: Automatic storage of prescriptions and chat history.
-   **Duplicate Detection**: Calculate SHA-256 hashes to instantly restore previously analyzed images.
-   **Multi-Page State**: Consistent data across "Analyzer" and "Smart Scheduler" workflows.

---

## 📂 Project Structure

```bash
.
├── app.py                # Main Streamlit application & router
├── backend/
│   ├── chain.py          # VisionChain logic (OCR -> Audit -> Schedule)
│   ├── prompt.py         # Multi-step medical prompts
├── db/                   # SQLite database & access logic
├── services/             # Core business logic (Extraction, Restoration)
├── scheduler/            # Schedule-specific logic and PDF export
├── frontend/
│   ├── pages/            # Page-specific orchestrators
│   ├── ui_components.py  # Shared UI elements
│   └── session_utils.py  # Shared session state management
└── README.md             # Project documentation
```

---

## ⚙️ Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd medical-prescription-analyzer-chatbot
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Configure Environment**:
    Create a `.env` file with your `QUBRID_API_KEY`.

4.  **Run the application**:
    ```bash
    uv run streamlit run app.py
    ```

---

## ⚠️ Disclaimer

**This tool is for informational and educational purposes only.** The analysis provided is AI-generated and should **not** be used for self-diagnosis or treatment. **Always verify any AI analysis with a qualified healthcare professional or pharmacist before taking any medication.**

---
*Powered by [Qubrid AI](https://www.qubrid.com/)*
