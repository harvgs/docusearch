# Railway Deployment Guide - Light Version (CPU-Only PyTorch)

## 🎯 Overview

This light version uses **CPU-only PyTorch** to achieve a deployment size of ~2.5-3GB, well within Railway's 4GB limit while maintaining full neural embedding capabilities.

## 📊 Size Comparison

| Component | Original | Light Version | Savings |
|-----------|----------|---------------|---------|
| PyTorch CUDA | ~4-5GB | ~1.5GB | 70% |
| Neural Model | ~1.5GB | ~90MB | 94% |
| **Total Image** | **~6.1GB** | **~2.5-3GB** | **60%** |

## 🚀 Quick Deployment Steps

### 1. Generate Light Embeddings
```bash
python generate_light_embeddings.py
```

### 2. Deploy to Railway
- Connect your GitHub repository to Railway
- Railway will automatically detect the Dockerfile
- Set environment variable: `OPENAI_API_KEY`

### 3. Monitor Deployment
- Check Railway logs for successful build
- Verify the app starts without errors

## 📁 File Structure

```
docusearch/
├── docusearch_light.py              # Main app (light version)
├── create_embeddings_light.py       # Light embedding processor
├── generate_light_embeddings.py     # Generation helper
├── requirements_ultra_minimal.txt   # CPU-only dependencies
├── Dockerfile                       # Multi-stage build
├── start.sh                         # Startup script
├── embeddings/
│   └── embeddings_light.json        # Generated embeddings
└── extracted_content/               # Your document data
```

## 🔧 Key Changes Made

### 1. CPU-Only PyTorch
```txt
torch>=2.0.0+cpu  # Instead of full CUDA version
```

### 2. Smallest Neural Model
```python
model_name="sentence-transformers/all-MiniLM-L6-v2"  # ~90MB vs ~1.5GB
```

### 3. Optimized for CPU
```python
device = "cpu"  # Force CPU usage
self.model.eval()  # Optimize for inference
```

## 💡 Benefits

- ✅ **Fits Railway limits**: ~2.5-3GB total
- ✅ **Full neural capabilities**: Better than TF-IDF
- ✅ **Fast startup**: No heavy model downloads
- ✅ **Cost-effective**: Smaller deployment = lower costs
- ✅ **Reliable**: No CUDA dependency issues

## 🔍 Performance

### Search Quality
- **Neural embeddings**: Understands context and synonyms
- **Small model**: Still provides good semantic search
- **CPU optimized**: Efficient inference on Railway

### Speed
- **Model loading**: ~90MB vs ~1.5GB
- **Inference**: CPU-optimized for Railway environment
- **Memory usage**: Minimal RAM requirements

## 🛠️ Troubleshooting

### Common Issues

1. **Build fails with CUDA errors**
   - Ensure `torch>=2.0.0+cpu` in requirements
   - Check Dockerfile uses correct requirements file

2. **Model download fails**
   - Check internet connectivity
   - Verify SSL settings in create_embeddings_light.py

3. **Memory issues**
   - Model is already optimized for minimal memory
   - Check Railway resource allocation

### Performance Tips

1. **Pre-generate embeddings**: Run locally before deployment
2. **Use cache directories**: Set to `/tmp/` for Railway
3. **Monitor logs**: Check Railway logs for any issues

## 📈 Next Steps

1. **Deploy and test**: Verify everything works on Railway
2. **Monitor performance**: Check search quality and speed
3. **Optimize further**: If needed, consider TF-IDF for even smaller size

## 🎉 Success Metrics

- ✅ Image size < 4GB
- ✅ App starts successfully
- ✅ Search functionality works
- ✅ Chat with documents works
- ✅ No CUDA-related errors

---

**Ready to deploy!** This light version gives you the best balance of performance and deployment size. 🚀