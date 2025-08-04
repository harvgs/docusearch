# Railway Port Fix

## 🚨 Issue
Railway deployment was failing with the error:
```
Error: Invalid value for '--server.port' (env var: 'STREAMLIT_SERVER_PORT'): '$PORT' is not a valid integer.
```

## 🔍 Root Cause
Railway was setting the `PORT` environment variable as a literal string `"$PORT"` instead of resolving it to the actual port number, causing Streamlit to fail when trying to parse it as an integer.

## 🔧 Solution Applied

### 1. **Updated `start_app.py`**
- Removed complex port parsing logic
- Hardcoded port to `8080` for Railway compatibility
- Simplified environment variable handling

### 2. **Created `start_simple.py`**
- Alternative startup script with minimal port handling
- Directly passes `'8080'` as string to Streamlit
- No environment variable parsing

### 3. **Updated Dockerfile**
- Added both startup scripts
- Exposed port 8080
- Provided alternative CMD option

## 📁 Files Modified

```
docusearch/
├── start_app.py          # ✅ Simplified port handling
├── start_simple.py       # ✅ New simple startup script
├── Dockerfile            # ✅ Added alternative startup option
└── RAILWAY_PORT_FIX.md   # ✅ This guide
```

## 🚀 Deployment Options

### Option 1: Use Updated `start_app.py` (Recommended)
```dockerfile
CMD ["python", "start_app.py"]
```

### Option 2: Use Simple Startup Script
```dockerfile
CMD ["python", "start_simple.py"]
```

## 🔍 Verification

After deployment, check Railway logs for:
```
🚀 Starting DocuSearch Light on port 8080
💻 Using CPU-only PyTorch for minimal deployment size
Running: python -m streamlit run docusearch_light.py --server.port 8080 --server.address 0.0.0.0
```

## 🛠️ Troubleshooting

If the issue persists:

1. **Check Railway Environment Variables**
   - Look for `PORT` variable in Railway dashboard
   - Ensure it's not set to `"$PORT"`

2. **Use Simple Startup Script**
   - Change Dockerfile CMD to use `start_simple.py`
   - Redeploy to Railway

3. **Manual Port Configuration**
   - Set `PORT=8080` in Railway environment variables
   - Or remove PORT variable entirely

## 🎯 Success Criteria

- ✅ App starts without port parsing errors
- ✅ Streamlit runs on port 8080
- ✅ Railway health checks pass
- ✅ App accessible via Railway URL

## 📊 Expected Behavior

1. **Startup:** Clean startup with hardcoded port
2. **Logs:** Clear port information in Railway logs
3. **Access:** App accessible at Railway-provided URL
4. **Health:** Health checks pass on port 8080

---

**The fix ensures Railway deployment works reliably by avoiding environment variable parsing issues and using a hardcoded port configuration.** 