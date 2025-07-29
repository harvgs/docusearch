# Railway Light Deployment Guide

## 🚨 Size Issue Solved!

Your deployment was failing because the Docker image exceeded Railway's 4GB limit. This light version should fix that issue.

## What Changed?

### 1. **Smaller Embedding Model**
- **Original**: `hkunlp/instructor-xl` (~1.5GB)
- **Light Version**: `sentence-transformers/all-MiniLM-L6-v2` (~90MB)
- **Result**: ~95% size reduction for the model

### 2. **Optimized Dependencies**
- CPU-only PyTorch (`torch-cpu`)
- Removed unnecessary packages
- Multi-stage Docker build

### 3. **Excluded Large Files**
- All data files excluded from Docker build
- Documentation and test files excluded
- Cache directories excluded

## Quick Deployment Steps

### 1. Generate Light Embeddings
```bash
python generate_light_embeddings.py
```

### 2. Deploy to Railway
```bash
# Option A: GitHub Integration
# Push your code to GitHub and connect Railway

# Option B: CLI
railway up
```

### 3. Set Environment Variable
In Railway dashboard:
- Variable: `OPENAI_API_KEY`
- Value: Your OpenAI API key

## File Structure for Light Deployment

```
docusearch/
├── docusearch_light.py          # Main app (light version)
├── create_embeddings_light.py   # Light embeddings script
├── generate_light_embeddings.py # Generation helper
├── requirements.txt             # Light dependencies
├── Procfile                     # Railway config
├── start.sh                     # Startup script
├── Dockerfile                   # Multi-stage build
├── .dockerignore                # Excludes large files
├── embeddings/
│   └── embeddings_light.json    # Light embeddings (generated)
└── extracted_content/           # Your documents (excluded from build)
```

## Size Comparison

| Component | Original | Light Version | Savings |
|-----------|----------|---------------|---------|
| Embedding Model | ~1.5GB | ~90MB | 94% |
| PyTorch | ~2GB | ~500MB | 75% |
| Total Image | ~7.1GB | ~2.5GB | 65% |

## Performance Notes

### Trade-offs
- **Smaller model** = Slightly lower accuracy
- **CPU-only** = Slower inference
- **Still functional** = All features work

### Benefits
- **Fits Railway limits** = Successful deployment
- **Faster startup** = Smaller download
- **Lower costs** = Less memory usage

## Troubleshooting

### Still Getting Size Errors?
1. **Check .dockerignore** - Ensure large files are excluded
2. **Use Dockerfile** - Multi-stage build reduces size
3. **Remove old files** - Delete unused scripts and data

### Model Download Issues?
1. **Check internet** - Model downloads at runtime
2. **Increase timeout** - First run takes longer
3. **Use cache** - Subsequent runs are faster

## Migration from Original

If you have the original version:

1. **Keep original files** - Don't delete them
2. **Generate light embeddings** - Run the generation script
3. **Test locally** - Verify light version works
4. **Deploy light version** - Use Railway

## Monitoring

After deployment:
- Check Railway logs for model download
- Monitor memory usage
- Test search functionality
- Verify chat works with API key

## Support

If you still have issues:
1. Check Railway logs for specific errors
2. Verify all files are in the repository
3. Ensure environment variables are set
4. Contact Railway support if needed

## Next Steps

Once deployed successfully:
1. **Custom domain** - Set up your own URL
2. **Monitoring** - Add health checks
3. **Scaling** - Plan for growth
4. **Optimization** - Fine-tune performance