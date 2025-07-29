# Enhanced Document Search and Chat

This is an enhanced version of the document search application that includes AI-powered chat functionality using GPT-4o-mini.

## Features

- **Search Mode**: Semantic search through your documents using embeddings
- **Chat Mode**: AI-powered conversations with your documents using GPT-4o-mini
- **Documents Mode**: Browse all documents organized by directory
- **Cost Tracking**: Monitor API usage costs
- **Download Links**: Access source documents directly

## Setup

### 1. Install Dependencies

```bash
conda activate chatbot
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

Edit `openai_config.json` and replace `"your-openai-api-key-here"` with your actual OpenAI API key:

```json
{
    "openai": {
        "api_key": "sk-your-actual-api-key-here"
    }
}
```

Alternatively, you can enter your API key directly in the app sidebar when you run it.

### 3. Run the Application

```bash
streamlit run docusearch_new.py
```

## Usage

### Search Mode
- Enter your search query
- View relevant documents with similarity scores
- Access source URLs and download original files

### Chat Mode
- Have natural conversations about your documents
- AI will search through your documents and provide contextual answers
- View sources used for each response
- Monitor API costs

### Documents Mode
- Browse all documents organized by directory
- See document previews and metadata
- Access source files directly

## Troubleshooting

### Missing Packages
If you see import errors, install the required packages:
```bash
pip install openai tiktoken
```

### API Key Issues
- Make sure your OpenAI API key is valid and has credits
- Check that you have access to GPT-4o-mini model
- Verify the API key is correctly entered in the config file or sidebar

### Embeddings Not Found
- Ensure you've run `create_embeddings.py` first to generate embeddings
- Check that `embeddings/embeddings.json` exists

## Cost Information

The chat mode uses GPT-4o-mini which costs:
- Input: $0.00015 per 1K tokens
- Output: $0.0006 per 1K tokens

Costs are tracked per interaction and for the entire session.

## Differences from streamlit_search.py

- **AI Chat**: Real conversational AI instead of just search results
- **Better UI**: More polished interface with cost tracking
- **Document browsing**: Organized view of all documents
- **Direct OpenAI API**: Simpler and more reliable than LangChain
- **Error handling**: Graceful fallbacks and better error messages