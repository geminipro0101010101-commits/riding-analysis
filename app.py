# app.py
import streamlit as st
import tempfile
import os
from process_video import process_ride_video
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Dhaka Ride Safety Analysis",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .top-header {
        background: linear-gradient(90deg, #1f77b4 0%, #2c5aa0 100%);
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .header-title {
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0;
    }
    .header-links {
        display: flex;
        gap: 1.5rem;
        align-items: center;
    }
    .header-link {
        color: white;
        text-decoration: none;
        font-size: 1rem;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        transition: background-color 0.3s;
    }
    .header-link:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    .verdict-safe {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #c3e6cb;
    }
    .verdict-moderate {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #ffeaa7;
    }
    .verdict-unsafe {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #f5c6cb;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .developer-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 2rem;
    }
    .contact-section {
        background-color: #e7f3ff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'show_contact' not in st.session_state:
    st.session_state.show_contact = False
if 'show_developer' not in st.session_state:
    st.session_state.show_developer = False

# Top Header with Navigation
st.markdown("""
    <div class="top-header">
        <div class="header-title">🏍️ Dhaka Ride Safety Analysis</div>
        <div class="header-links">
            <a href="#contact" class="header-link" onclick="document.getElementById('contact-section').scrollIntoView(); return false;">📧 Contact</a>
            <a href="#developer" class="header-link" onclick="document.getElementById('developer-section').scrollIntoView(); return false;">👨‍💻 Developer</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<h1 class="main-header">🏍️ DHAKA RIDE SAFETY ANALYSIS</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Motorcycle Safety Scoring System for Dhaka City</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📋 About")
    st.info("""
    **Dhaka Ride Safety Analysis** uses computer vision and AI to analyze 
    motorcycle riding videos and detect risky behaviors specific to Dhaka traffic.
    
    **Features:**
    - 20+ hazard detectors
    - Real-time risk assessment
    - Personalized recommendations
    - Dhaka-specific traffic patterns
    """)
    
    st.header("📤 Upload Video")
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help="Upload a motorcycle riding video for analysis"
    )
    
    if uploaded_file is not None:
        if st.button("🚀 Analyze Video", type="primary", use_container_width=True):
            st.session_state.processing = True
            st.session_state.results = None
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name
            
            try:
                # Process video with progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Initializing models...")
                progress_bar.progress(10)
                
                status_text.text("Processing video frames...")
                progress_bar.progress(30)
                
                results = process_ride_video(tmp_path)
                progress_bar.progress(70)
                
                status_text.text("Generating recommendations...")
                progress_bar.progress(90)
                
                if results:
                    st.session_state.results = results
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    st.success("Video analyzed successfully!")
                else:
                    st.error("Failed to process video. Please check the file format.")
                
            except Exception as e:
                st.error(f"Error processing video: {str(e)}")
            finally:
                # Cleanup
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                st.session_state.processing = False
                progress_bar.empty()
                status_text.empty()
    
    st.markdown("---")
    st.markdown("### Quick Links")
    if st.button("📧 Contact Us", use_container_width=True):
        st.session_state.show_contact = True
        st.session_state.show_developer = False
    if st.button("👨‍💻 Developer Info", use_container_width=True):
        st.session_state.show_developer = True
        st.session_state.show_contact = False

# Contact Section
if st.session_state.show_contact:
    st.markdown('<div id="contact-section"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("## 📧 Contact Us")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="contact-section">
            <h3>Get in Touch</h3>
            <p>Have questions, feedback, or need support? We're here to help!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Contact Information")
        st.markdown("""
        **Email:** support@dhakarideanalysis.com  
        **Phone:** +880-XXX-XXXXXXX  
        **Address:** Dhaka, Bangladesh
        """)
        
        st.markdown("### Support Hours")
        st.markdown("""
        - **Monday - Friday:** 9:00 AM - 6:00 PM (BST)
        - **Saturday:** 10:00 AM - 4:00 PM (BST)
        - **Sunday:** Closed
        """)
    
    with col2:
        st.markdown("### Send us a Message")
        with st.form("contact_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            subject = st.selectbox("Subject", [
                "General Inquiry",
                "Technical Support",
                "Feature Request",
                "Bug Report",
                "Partnership",
                "Other"
            ])
            message = st.text_area("Message", height=150)
            submitted = st.form_submit_button("Send Message", type="primary")
            
            if submitted:
                if name and email and message:
                    st.success(f"Thank you {name}! Your message has been sent. We'll get back to you at {email} soon.")
                else:
                    st.warning("Please fill in all required fields.")
    
    st.markdown("### Social Media")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("[📘 Facebook](https://facebook.com)")
    with col2:
        st.markdown("[🐦 Twitter](https://twitter.com)")
    with col3:
        st.markdown("[💼 LinkedIn](https://linkedin.com)")
    with col4:
        st.markdown("[📷 Instagram](https://instagram.com)")

# Developer Section
if st.session_state.show_developer:
    st.markdown('<div id="developer-section"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("## 👨‍💻 Developer Information")
    
    st.markdown("""
    <div class="developer-section">
        <h3>About the Project</h3>
        <p>Dhaka Ride Safety Analysis is an AI-powered system designed to improve motorcycle safety 
        in Dhaka city through computer vision and machine learning.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛠️ Technology Stack")
        st.markdown("""
        - **Computer Vision:** OpenCV, YOLOv8
        - **Machine Learning:** scikit-learn, Decision Trees
        - **Web Framework:** Streamlit
        - **Data Processing:** NumPy, Pandas
        - **Visualization:** Plotly
        - **Language:** Python 3.8+
        """)
        
        st.markdown("### 📊 System Architecture")
        st.markdown("""
        - **Video Processing:** Optical flow analysis
        - **Object Detection:** YOLOv8 for vehicle/pedestrian detection
        - **Risk Assessment:** 20+ hazard detectors
        - **Recommendation Engine:** Context-aware suggestions
        """)
    
    with col2:
        st.markdown("### 🎯 Key Features")
        st.markdown("""
        - Real-time video analysis
        - 20+ hazard pattern detection
        - Dhaka-specific traffic pattern recognition
        - Personalized safety recommendations
        - Comprehensive risk scoring
        - Detailed analytics dashboard
        """)
        
        st.markdown("### 📈 Performance Metrics")
        st.markdown("""
        - Processing Speed: ~100-150ms per frame
        - Detection Accuracy: Optimized for Dhaka traffic
        - Supported Formats: MP4, AVI, MOV, MKV
        - Max Video Size: 200MB (Streamlit Cloud)
        """)
    
    st.markdown("### 👥 Development Team")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Lead Developer**  
        [Your Name]  
        📧 developer@dhakarideanalysis.com  
        🔗 [GitHub Profile](https://github.com)
        """)
    
    with col2:
        st.markdown("""
        **AI/ML Engineer**  
        [Team Member]  
        📧 ml@dhakarideanalysis.com  
        🔗 [LinkedIn](https://linkedin.com)
        """)
    
    with col3:
        st.markdown("""
        **Computer Vision Specialist**  
        [Team Member]  
        📧 cv@dhakarideanalysis.com  
        🔗 [Portfolio](https://portfolio.com)
        """)
    
    st.markdown("### 📚 Documentation")
    st.markdown("""
    - [System Architecture](SYSTEM_ARCHITECTURE.md)
    - [Quick Start Guide](QUICKSTART.md)
    - [API Documentation](README.md)
    - [GitHub Repository](https://github.com/your-repo)
    """)
    
    st.markdown("### 🤝 Contributing")
    st.info("""
    We welcome contributions! If you'd like to contribute to this project, please:
    1. Fork the repository
    2. Create a feature branch
    3. Submit a pull request
    
    For major changes, please open an issue first to discuss what you would like to change.
    """)
    
    st.markdown("### 📄 License")
    st.markdown("""
    This project is licensed under the MIT License - see the LICENSE file for details.
    """)

# Main content area
if st.session_state.processing:
    st.info("⏳ Processing video... This may take a few minutes depending on video length.")
    
elif st.session_state.results:
    results = st.session_state.results
    
    # Verdict Section
    st.markdown("---")
    verdict = results['verdict']
    verdict_color = {
        'SAFE': 'verdict-safe',
        'CAUTION': 'verdict-moderate',
        'MODERATE RISK': 'verdict-moderate',
        'UNSAFE': 'verdict-unsafe'
    }.get(verdict, 'verdict-safe')
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f'<div class="{verdict_color}">', unsafe_allow_html=True)
        st.markdown(f"### 🎯 RIDE STATUS: {verdict}")
        st.markdown(f"**{results['reason']}**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.metric("Risk Percentage", f"{results['risk_percentage']:.1f}%")
        st.metric("Critical Events", f"{results['critical_frames']}/{results['total_samples']}")
        st.metric("Safe Frames", results['safe_frames'])
    
    # Rider Behavior Profile
    st.markdown("---")
    st.subheader("👤 Rider Behavior Profile")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Style:** {results['rider_style']}")
    with col2:
        st.markdown(f"**Analysis:** {results['style_analysis']}")
    
    # Statistics Dashboard
    st.markdown("---")
    st.subheader("📊 Risk Statistics")
    
    # Filter non-zero stats
    non_zero_stats = {k: v for k, v in results['stats'].items() if v > 0}
    
    if non_zero_stats:
        # Create two columns for stats
        col1, col2 = st.columns(2)
        
        stats_items = list(non_zero_stats.items())
        mid_point = len(stats_items) // 2
        
        with col1:
            for key, value in stats_items[:mid_point]:
                st.metric(key, value)
        
        with col2:
            for key, value in stats_items[mid_point:]:
                st.metric(key, value)
        
        # Bar chart
        st.markdown("#### Risk Events Breakdown")
        df_stats = pd.DataFrame(list(non_zero_stats.items()), columns=['Risk Type', 'Count'])
        fig = px.bar(
            df_stats, 
            x='Count', 
            y='Risk Type',
            orientation='h',
            color='Count',
            color_continuous_scale='Reds',
            title="Detected Risk Events"
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("✅ No risk events detected! Excellent riding.")
    
    # Critical Events Timeline
    if results['critical_events']:
        st.markdown("---")
        st.subheader("⚠️ Critical Events Timeline")
        
        events_df = pd.DataFrame(results['critical_events'])
        st.dataframe(
            events_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "frame_id": "Frame ID",
                "risk_label": "Risk Level",
                "description": "Event Description"
            }
        )
    
    # Recommendations
    st.markdown("---")
    st.subheader("💡 Actionable Recommendations")
    
    # Group recommendations by category
    recs_by_category = {}
    for category, title, solution in results['recommendations']:
        if category not in recs_by_category:
            recs_by_category[category] = []
        recs_by_category[category].append((title, solution))
    
    # Display recommendations
    category_icons = {
        'CRITICAL': '🔴',
        'WARNING': '🟡',
        'IMPROVEMENT': '🔵',
        'AWARENESS': '🟢',
        'ACHIEVEMENT': '⭐',
        'OPTIMIZATION': '⚡',
        'MASTERY': '🏆',
        'COMMUNITY': '🤝',
        'General Dhaka Tips': '📚'
    }
    
    for category, recs in recs_by_category.items():
        icon = category_icons.get(category, '📌')
        st.markdown(f"### {icon} {category}")
        
        for title, solution in recs:
            with st.expander(f"**{title}**"):
                st.write(solution)
    
    # Download Report
    st.markdown("---")
    st.subheader("📥 Download Report")
    
    # Generate text report
    report_text = f"""
DHAKA-RIDE SAFETY REPORT
========================

RIDE STATUS: {results['verdict']}
REASON: {results['reason']}

RISK SUMMARY
============
Total Samples Analyzed: {results['total_samples']}
Safe Frames: {results['safe_frames']}
Critical Events: {results['critical_frames']}
Risk Percentage: {results['risk_percentage']:.1f}%

RIDER BEHAVIOR PROFILE
======================
Style: {results['rider_style']}
Analysis: {results['style_analysis']}

STATISTICS BREAKDOWN
====================
"""
    for key, value in results['stats'].items():
        report_text += f"{key}: {value}\n"
    
    report_text += "\n\nCRITICAL EVENTS\n"
    report_text += "=" * 40 + "\n"
    for event in results['critical_events']:
        report_text += f"[Frame {event['frame_id']}] {event['risk_label']}: {event['description']}\n"
    
    report_text += "\n\nRECOMMENDATIONS\n"
    report_text += "=" * 40 + "\n"
    for category, title, solution in results['recommendations']:
        report_text += f"\n[{category}] {title}\n{solution}\n"
    
    st.download_button(
        label="📄 Download Full Report (TXT)",
        data=report_text,
        file_name="ride_safety_report.txt",
        mime="text/plain"
    )
    
else:
    # Welcome screen
    st.info("👈 Please upload a video file in the sidebar to begin analysis.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        ### 🎯 Features
        - Real-time hazard detection
        - 20+ risk indicators
        - Personalized feedback
        - Dhaka-specific patterns
        """)
    
    with col2:
        st.markdown("""
        ### 🔍 Detections
        - Pinch points
        - Aggressive maneuvers
        - Traffic violations
        - Distraction detection
        """)
    
    with col3:
        st.markdown("""
        ### 📈 Benefits
        - Improve riding safety
        - Learn from mistakes
        - Track progress
        - Reduce accidents
        """)

