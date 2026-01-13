# Medical Prescription Analyzer Chatbot 💊

A production-grade, structured medical intelligence platform powered by **Qubrid AI**, **LangChain**, and **Streamlit**. This assistant specializes in analyzing medical prescriptions (handwritten or digital) through a multi-step vision reasoning pipeline, extracting structured data, and providing focused medical insights through various chat modes.

---

## 🚀 Key Features

### 🔍 4-Step Medical Reasoning Pipeline
The core of the application is a robust backend pipeline that processes prescription images:
1.  **Vision OCR Extraction**: Transcribes every piece of text from the image, focusing on medicine names and dosages.
2.  **Entity Normalization**: Converts raw text into a structured JSON schema (patient, doctor, date, medicines, timing, duration).
3.  **Ambiguity Audit**: Identifies low-confidence extractions or missing information and flags them for user clarification.
4.  **Safety Audit**: Performs a safety check on extracted instructions and conflicting timings.

### 💬 Focused Medical Chat Modes
Users can interact with the analyzed prescription using specialized modes:
-   **🩺 Explain Prescription**: Provides a general explanation of each medicine's purpose and how to take it.
-   **⏰ Create Schedule**: Generates a simple daily/hourly medication schedule for the patient.
-   **⚠️ Safety Check**: Highlights precautions, side effects, and common contraindications (e.g., "Avoid alcohol").
-   **📄 Summary for Caregiver**: Produces a concise, factual bullet-point summary for patient care.

### 🛡️ Interactive Safety & Transparency
-   **Medicine Cards**: Visualized extracted data with confidence-based color coding (Green/Orange/Red).
-   **Ambiguity Resolver**: Interactive UI components that allow users to clarify handwriting uncertainties identified by the AI.
-   **AI Transparency Panel**: Displays the underlying model name and active reasoning steps for clinical transparency.

---

## 🛠️ Technology Stack

-   **Model Architecture**: Qubrid AI Vision LLM (Optimized for medical reasoning).
-   **Orchestration**: [LangChain](https://www.langchain.com/) for memory management and chain logic.
-   **Frontend**: [Streamlit](https://streamlit.io/) for a clean, responsive medical interface.
-   **Image Processing**: PIL (Pillow) for image handling and base64 encoding for API transfer.

---

## 📂 Project Structure

```bash
.
├── app.py                # Main Streamlit application & state management
├── backend/
│   ├── chain.py          # VisionChain logic (OCR -> Audit execution)
│   ├── qubrid_client.py  # Custom LLM wrapper for Qubrid AI API
│   ├── prompt.py         # Multi-step medical prompts & chat modes
│   └── utils.py          # Image processing and API helpers
├── frontend/
│   ├── ui_components.py  # Modular UI elements (sidebar, cards, resolver)
│   └── assets/           # UI assets and logos
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
    (Recommended: Use `uv` for faster installation)
    ```bash
    uv sync
    ```

3.  **Configure Environment**:
    Create a `.env` file in the root directory and add your Qubrid AI credentials:
    ```env
    QUBRID_API_KEY=your_api_key_here
    ```

4.  **Run the application**:
    ```bash
    uv run streamlit run app.py
    ```

---

## ⚠️ Disclaimer

**This tool is for informational and educational purposes only.** The analysis provided is AI-generated and should **not** be used for self-diagnosis or as a substitute for professional medical advice, diagnosis, or treatment. **Always verify any AI analysis with a qualified healthcare professional or pharmacist before taking any medication.**

---
*Powered by [Qubrid AI](https://www.qubrid.com/)*
