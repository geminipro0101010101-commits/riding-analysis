# Streamlit Deployment Guide

## 📋 Files Created

1. **app.py** - Main Streamlit application with UI
2. **process_video.py** - Refactored processing logic (returns data instead of writing to file)
3. **requirements.txt** - All required dependencies
4. **.streamlit/config.toml** - Streamlit configuration

## 🚀 Quick Start

### Local Deployment

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   streamlit run app.py
   ```

3. **Access the app:**
   - The app will automatically open in your browser
   - Default URL: `http://localhost:8501`

## 🌐 Streamlit Cloud Deployment

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit - Streamlit app"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`
6. Click "Deploy"

## ✨ Features

### UI Components

1. **Top Header Navigation**
   - Contact section link
   - Developer section link
   - Professional gradient design

2. **Contact Section**
   - Contact form
   - Contact information
   - Support hours
   - Social media links

3. **Developer Section**
   - Technology stack
   - System architecture
   - Development team info
   - Documentation links
   - Contributing guidelines

4. **Main Dashboard**
   - Video upload widget
   - Progress indicators
   - Verdict display (color-coded)
   - Statistics cards
   - Interactive charts
   - Recommendations
   - Downloadable report

## 🎨 Customization

### Update Contact Information

Edit `app.py` and modify the contact section:
```python
**Email:** your-email@example.com
**Phone:** +880-XXX-XXXXXXX
**Address:** Your Address
```

### Update Developer Information

Edit the developer section in `app.py`:
- Team member names
- Email addresses
- Social media links
- GitHub repository URL

### Change Theme Colors

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"  # Change to your brand color
```

## 📝 Notes

- **File Size Limit:** 200MB per video (Streamlit Cloud)
- **Processing Time:** Depends on video length (typically 2-5 minutes for 1-minute video)
- **Browser Compatibility:** Works on Chrome, Firefox, Safari, Edge

## 🔧 Troubleshooting

### Issue: "Module not found"
**Solution:** Install all dependencies: `pip install -r requirements.txt`

### Issue: "Video processing fails"
**Solution:** Check video format (MP4, AVI, MOV, MKV supported)

### Issue: "Memory error"
**Solution:** Use shorter videos or increase system memory

## 📞 Support

For issues or questions, use the Contact section in the app or open an issue on GitHub.

