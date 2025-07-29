# DocuSearch - Railway Deployment Guide

This guide will help you deploy the DocuSearch application on Railway.

## What is DocuSearch?

DocuSearch is a document search and chat application that uses:
- **Embeddings**: HuggingFace's `hkunlp/instructor-xl` model for document embeddings
- **Chat**: OpenAI's GPT-4o-mini for conversational responses
- **UI**: Streamlit for the web interface

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **OpenAI API Key**: Get one from [OpenAI Platform](https://platform.openai.com/api-keys)
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Deployment Steps

### 1. Prepare Your Repository

Make sure your repository contains these files:
- `docusearch_new.py` - Main Streamlit application
- `create_embeddings.py` - Embedding creation script
- `requirements.txt` - Python dependencies
- `Procfile` - Railway deployment configuration
- `railway.json` - Railway-specific settings
- `.dockerignore` - Build optimization

### 2. Deploy to Railway

#### Option A: Deploy from GitHub

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect it's a Python project

#### Option B: Deploy from CLI

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Initialize and deploy:
   ```bash
   railway init
   railway up
   ```

### 3. Configure Environment Variables

In your Railway project dashboard:

1. Go to the "Variables" tab
2. Add the following environment variable:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: Your OpenAI API key

### 4. Deploy Your Data

You have two options for your embeddings and documents:

#### Option A: Include in Repository (Recommended for small datasets)
- Keep your `embeddings/embeddings.json` file in the repository
- Keep your `extracted_content/` directory in the repository

#### Option B: Upload After Deployment
- Deploy without the data files first
- Use Railway's file system or external storage (S3, etc.)
- Update the file paths in your code accordingly

### 5. Monitor Deployment

1. Check the "Deployments" tab in Railway dashboard
2. View logs for any errors
3. Once deployed, Railway will provide a public URL

## Configuration Files

### Procfile
```
web: streamlit run docusearch_new.py --server.port=$PORT --server.address=0.0.0.0
```

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run docusearch_new.py --server.port=$PORT --server.address=0.0.0.0",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check that all dependencies are in `requirements.txt`
   - Ensure Python version compatibility
   - Check Railway logs for specific error messages

2. **Memory Issues**
   - The embedding model requires significant memory
   - Consider upgrading your Railway plan if needed
   - Optimize by reducing batch sizes in `create_embeddings.py`

3. **API Key Issues**
   - Ensure `OPENAI_API_KEY` is set in Railway environment variables
   - Check that the API key is valid and has sufficient credits

4. **File Path Issues**
   - Use relative paths in your code
   - Ensure data files are included in the repository or uploaded separately

### Performance Optimization

1. **Reduce Model Size**: Consider using a smaller embedding model
2. **Caching**: Implement caching for embeddings and search results
3. **Batch Processing**: Process documents in smaller batches
4. **CDN**: Use a CDN for static assets

## Cost Considerations

- **Railway**: Pay-per-use pricing based on compute and bandwidth
- **OpenAI**: Pay-per-token for API calls
- **Embedding Model**: Free (HuggingFace models)

## Security Notes

1. **API Keys**: Never commit API keys to your repository
2. **Environment Variables**: Use Railway's environment variable system
3. **Data Privacy**: Ensure your documents don't contain sensitive information
4. **Rate Limiting**: Implement rate limiting for production use

## Support

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **OpenAI Documentation**: [platform.openai.com/docs](https://platform.openai.com/docs)

## Next Steps

After successful deployment:

1. **Custom Domain**: Set up a custom domain in Railway
2. **Monitoring**: Set up monitoring and alerting
3. **Backup**: Implement regular backups of your data
4. **Scaling**: Plan for scaling as your user base grows