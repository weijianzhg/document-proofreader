# AI-Powered Document Proofreader

A Streamlit-based web application that uses OpenAI's GPT-4 to automatically proofread and improve Word documents (.docx files). The application provides an intuitive interface for uploading documents, reviewing AI-suggested changes, and downloading the corrected versions.

## Features

- **Document Upload**: Support for Word documents (.docx format)
- **AI-Powered Proofreading**: Uses OpenAI's GPT-4 for intelligent grammar, spelling, and style corrections
- **Interactive Review**: Review each suggested change with visual diff highlighting
- **Manual Editing**: Make additional edits to AI-corrected text
- **Change Approval**: Selectively approve or reject individual changes
- **Multiple Output Formats**: Download clean corrected documents or versions with tracked changes
- **Token Management**: Automatic text chunking for long documents to handle API token limits
- **Document Statistics**: View word count, paragraph count, and other document metrics

## Prerequisites

- Python 3.11 or higher
- OpenAI API key

## Installation

### Prerequisites
- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager

1. Install uv if you haven't already:
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip
pip install uv
```

2. Clone the repository:
```bash
git clone https://github.com/weijianzhg/document-proofreader
cd document-proofreader
```

3. Install dependencies:
```bash
uv sync
```

4. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

1. Start the Streamlit application:
```bash
uv run streamlit run app.py
```

2. Open your web browser and navigate to `http://localhost:8501`

3. Upload a Word document (.docx file)

4. Wait for the AI to process and proofread your document

5. Review the suggested changes:
   - View highlighted differences between original and corrected text
   - Make additional manual edits if needed
   - Approve or reject individual changes

6. Download your corrected document in your preferred format

## How It Works

### Document Processing
- Extracts text from Word documents while preserving formatting
- Splits long documents into manageable chunks for API processing
- Maintains paragraph structure and basic formatting

### AI Proofreading
- Uses GPT-4 for intelligent text correction
- Focuses on grammar, spelling, punctuation, and clarity improvements
- Maintains original meaning and writing style
- Handles documents of any length through automatic chunking

### Review Interface
- Visual diff highlighting shows exactly what changed
- Interactive approval system for granular control
- Manual editing capabilities for further refinements
- Real-time document statistics and progress tracking


## License

MIT