# Document Analyzer

A tool that uses Google's Gemini AI to analyze documents (PDFs and images) and extract or summarize their content.

## Features

- Extract full text from PDF documents and images
- Generate summaries of document content
- Support for both Arabic and English languages
- Save output as text files or Word documents
- User-friendly GUI interface

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Setup Instructions

1. Clone this repository or download the files to your local machine:

```bash
git clone https://github.com/if12is/Document-Analyzer.git
cd document_analyzer
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
```

3. Activate the virtual environment:

   - Windows:

   ```bash
   venv\Scripts\activate
   ```

   - macOS/Linux:

   ```bash
   source venv/bin/activate
   ```

4. Install the required dependencies:

```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the project root with your Google API key:

```bash
# .env
GOOGLE_API_KEY=`your_google_api_key_here`
GEMINI_MODEL=`your_gemini_model_here`
```

6. Run the application:

```bash
python app.py
```
