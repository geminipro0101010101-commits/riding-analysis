# QUICK START GUIDE

## 1. Prerequisites
- Python 3.8+
- OpenCV (`pip install opencv-python`)
- NumPy (`pip install numpy`)
- scikit-learn (`pip install scikit-learn`)
- Ultralytics YOLOv8 (`pip install ultralytics`)
- Video file at: `G:\Capstone c\Videos\video 1.mp4`

## 2. Installation
```powershell
cd "g:\Capstone c\Risk Analysis"
pip install opencv-python numpy scikit-learn ultralytics
```

## 3. Run Analysis
```powershell
python main.py
```

## 4. View Report
Open `ride_safety_report.txt` to see:
- Critical events detected
- Rider behavior profile (Reactive/Proactive)
- Risk verdict (SAFE / MODERATE / UNSAFE)
- 23 personalized recommendations

## 5. Expected Output

```
--- DHAKA-RIDE PROTOCOL (Logic-First) ---

[1/4] Processing Video: G:\Capstone c\Videos\video 1.mp4...
[2/4] Generating Dhaka-Context Descriptions...
[3/4] Predicting Risk Levels...

Success! Report saved to ride_safety_report.txt
Critical Events: 12 / 47
Reactive Swerves: 8
Pinch Points: 3
```

## 6. Report Sections

### CRITICAL EVENTS
```
[Frame 145] DANGER: reactive_swerve tailgating_critical
[Frame 203] DANGER: critical_pinch_point heavy_vehicle_conflict
```

### RIDER BEHAVIOR PROFILE
```
STYLE: REACTIVE (High Risk)
Analysis: Rider relies on last-second swerves rather than planning ahead.
```

### FINAL VERDICT
```
RIDE STATUS: UNSAFE
REASON: Frequent reactive swerving detected (8 instances).
```

### ACTIONABLE RECOMMENDATIONS
```
🚨 CRITICAL ACTIONS (Do This Today)
- 3-Second Rule Drill
- Phone Lockout Challenge

⚠️ WARNING (Next Ride)
- 'Leguna' Awareness Training

📚 DHAKA SURVIVAL TIPS (Daily Reminder)
- The 'Look-Look-Go' Rule
```

## 7. What Each Module Does

| Module | Function |
|--------|----------|
| `video_processor.py` | Extracts jerk, pinch points, vehicle types |
| `text_generator.py` | Creates semantic tokens from frame data |
| `risk_model.py` | Classifies tokens (SAFE/MODERATE/CRITICAL) |
| `recommendations.py` | Maps verdicts to 23 solutions |
| `main.py` | Runs the full pipeline |

## 8. Customize

### Change Video Path
Edit line 8 in `main.py`:
```python
video_path = r"C:\path\to\your\video.mp4"
```

### Adjust Thresholds
Edit `video_processor.py`:
```python
jerk_threshold = 1.5  # Default
pinch_threshold = frame_width * 0.30  # Default (30%)
```

### Change Sample Rate
Edit line 11 in `main.py`:
```python
processor = VideoProcessor(video_path, window_size=10)  # Increase for faster processing
```

## 9. Troubleshooting

**Video not found?**
```
Error: [1/4] Processing Video...
```
→ Check video path and file exists

**YOLO model not found?**
```
Error: OSError: yolov8n.pt
```
→ Ensure `yolov8n.pt` is in the project folder (or let YOLO auto-download)

**Report not generated?**
```
No critical events detected
```
→ Check video quality and lighting. Ensure at least 1 hazardous behavior detected.

## 10. Example Scenarios

### Scenario 1: Safe Rider
```
Verdict: SAFE
Reactive Swerves: 0
Pinch Points: 0
→ Gets: Achievement badges + route optimization tips
```

### Scenario 2: Reactive Rider
```
Verdict: UNSAFE
Reactive Swerves: 8
Tailgating: 5
→ Gets: Critical 3-second rule drill, cooling period, awareness training
```

### Scenario 3: Phone Distracted
```
Verdict: UNSAFE (Auto)
Distracted Riding: 1+
→ Gets: Immediate phone lockout challenge
```

---

## Performance Notes

- **Processing Speed**: ~5-10 seconds per minute of video (depends on resolution)
- **Video Resolution**: Works with 720p to 1080p
- **FPS**: Works with 24, 30, or 60 fps
- **Frame Sampling**: Random selection in 10-frame windows (avoids processing every frame)

---

## Output Files

```
ride_safety_report.txt  - Full safety analysis (auto-generated)
test_recommendations.py - Unit test for recommendation engine
README.md              - Full documentation
IMPLEMENTATION.md      - Technical details
```

---

**Ready to analyze your first Dhaka ride!** 🏍️
