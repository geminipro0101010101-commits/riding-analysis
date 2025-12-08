# DHAKA-RIDE SAFETY ANALYSIS SYSTEM
## Logic-First Motorcycle Safety Scoring (No GPS Required)

---

## Overview

DHAKA-RIDE is a computer-vision-based motorcycle safety scoring system designed specifically for Dhaka city traffic. It analyzes video footage of motorcycle rides to detect reactive vs. proactive behavior, identify high-risk adjacency (pinch points), and provide actionable recommendations tailored to Dhaka-specific hazards.

**Key Innovation**: Uses **optical flow** (pixel motion) to calculate jerk and detect unsafe swerving patterns without requiring GPS, speedometer, or absolute speed data.

---

## System Architecture

### 1. **video_processor.py** - Vision Analysis
- **Optical Flow**: Farneback algorithm to calculate pixel motion
- **Jerk Metric**: Sudden lateral movement (reactive swerving indicator)
- **Pinch Point Detection**: Calculates center-lane gap between obstacles
- **Vehicle Classification**: Heuristic-based rickshaw/CNG detection using bounding box aspect ratios
- **Output**: Frame-level data with jerk, proximity, speed proxy, and risk flags

### 2. **text_generator.py** - Semantic Token Generation
- Converts raw frame data into human-interpretable risk tokens
- 6 context layers:
  - **Speed**: Stationary/Slow/Fast (traffic jam exemption logic)
  - **Behavior**: Reactive swerve vs. proactive braking
  - **Space**: Pinch point detection (gap width < 30% frame)
  - **Objects**: Rickshaw/CNG/Heavy vehicle identification
  - **Proximity**: Tailgating risk (proximity > 0.4 = very close)
  - **Environment**: Glare/visibility issues

### 3. **risk_model.py** - Decision Tree Classifier
- Trains on 11 semantic descriptions → 3 risk levels
- **SAFE (0)**: Traffic jam + stable control
- **MODERATE (1)**: Occasional hazards
- **CRITICAL (2)**: Reactive swerving, confinement, distraction
- Uses sklearn CountVectorizer + DecisionTreeClassifier

### 4. **recommendations.py** - Actionable Solutions
- 23 specific recommendations across 4 categories:
  - **UNSAFE**: Critical interventions (3-second rule, phone lockout, escape route replay)
  - **MODERATE**: Improvement tips (smoothness score, rickshaw prediction)
  - **SAFE**: Achievement badges, route optimization, community contribution
  - **General**: Universal Dhaka traffic survival tips
- Triggered by detected behaviors (reactive swerves, pinch points, distraction, etc.)

### 5. **main.py** - Orchestration
- Processes video frames
- Generates descriptions
- Predicts risk levels
- Produces comprehensive safety report with recommendations

---

## Key Features

### Jerk Metric (Reactive vs. Proactive)
```
jerk = |current_lateral_flow_x - previous_lateral_flow_x|

IF jerk > threshold AND critical TTC:
  → REACTIVE_SWERVE (high risk)
ELSE:
  → PROACTIVE_BRAKING (safe)
```
- Measures sudden lateral movement (panic swerves)
- Scaled by frame width for cross-camera robustness
- Threshold: 0.15% of frame width

### Pinch Point Logic
```
center_gap = right_obstacle_left_edge - left_obstacle_right_edge

IF center_gap < 30% of frame_width AND speed != stationary:
  → CRITICAL_PINCH_POINT
```
- Detects rider sandwiched between buses/trucks
- Traffic jams (stationary) exempt from critical flag
- Specific to Dhaka filtering patterns

### Vehicle Classification
```
aspect_ratio = bbox_width / bbox_height

IF label = "bicycle" AND aspect_ratio > 0.6:
  → Reclassify as "rickshaw"
  
IF label = "car" AND width < height * 1.1:
  → Reclassify as "cng"
```
- Uses shape heuristics (rickshaws are wider, CNGs are narrow)
- Improves Dhaka-specific hazard detection

### Traffic Jam Exemption
- Close proximity + stationary/slow speed = SAFE (not critical)
- Reflects Dhaka reality where filtering is normal in congestion
- Prevents false positives on slow-moving bumper-to-bumper traffic

---

## Usage

### Basic Run
```powershell
python main.py
```

### Input
- Video file path: `G:\Capstone c\Videos\video 1.mp4`
- Model: YOLOv8n (pre-trained on COCO dataset)
- Sampling: Random frames at window_size=10 intervals

### Output
- **ride_safety_report.txt** with:
  - Critical events log
  - Rider behavior profile (Reactive/Proactive)
  - Risk summary and verdict (SAFE / MODERATE RISK / UNSAFE)
  - Actionable recommendations (23 possible)
  - Dhaka survival tips

---

## Recommendations System (23 Solutions)

### Category A: UNSAFE (Critical)
1. **3-Second Rule Drill** - Tailgating fix
2. **Escape Route Replay** - Pinch point visualization
3. **Phone Lockout Challenge** - Distraction recovery
4. **'Leguna' Awareness** - Heavy vehicle braking
5. **Blind Spot Visualizer** - Bus/truck safety zones
6. **Glare Recovery Tips** - Visibility management
7. **Mandatory Cooling Period** - Fatigue detection

### Category B: MODERATE (Improvement)
8. **Smoothness Score** - Jerk reduction gamification
9. **Rickshaw Prediction Module** - Unpredictable behavior
10. **Pinch Point Warning** - Gap safety threshold
11. **Intersection Scanner** - Safe entry logic
12. **Edge Trap Alert** - Curb hazards
13. **Late-Night Speed Cap** - Darkness adaptation
14. **Horn vs. Brake Analysis** - Reaction priority

### Category C: SAFE (Achievement)
15. **Safety Streak Badge** - Zero incidents milestone
16. **Insurance Certificate** - Top performer recognition
17. **Route Optimization** - Alternative route suggestions
18. **Defensive Mentor Status** - Shadow riding opportunity
19. **Pothole Contribution** - Community hazard reporting

### Category D: General Tips (Always Shown)
20. **Look-Look-Go Rule** - Wrong-way rickshaws
21. **CNG Cage Awareness** - Blind spot safety
22. **Pedestrian Dark Mode** - Night crossing hazards
23. **Sandwich Exit Strategy** - Multi-bus escapes

---

## Verdict Logic

| Condition | Verdict |
|-----------|---------|
| Phone distraction detected | UNSAFE |
| Reactive Swerves > 5 | UNSAFE |
| Critical risk % > 15% | UNSAFE |
| Critical risk % > 5% | MODERATE RISK |
| Else | SAFE |

---

## Technical Specifications

### Optical Flow
- **Algorithm**: Farneback (cv2.calcOpticalFlowFarneback)
- **Window**: 0.5 pyramid scale, 3 levels, 15×15 neighborhood
- **Output**: X/Y pixel motion per frame

### YOLO Detection
- **Model**: YOLOv8n (nano, 3.2M parameters)
- **Classes Used**: 0=person, 1=bicycle, 2=car, 3=motorcycle, 5=bus, 7=truck, 67=phone
- **Relevant**: [0, 1, 2, 3, 5, 7, 67]

### Sampling Strategy
- **Window Size**: 10 frames per sample
- **Method**: Random frame selection within each window
- **Advantage**: Covers ride without processing every frame

---

## Thresholds & Tuning

| Parameter | Value | Notes |
|-----------|-------|-------|
| Speed proxy (slow→fast) | 15 pixels | Adjust for video FPS/resolution |
| Jerk threshold | 0.15% frame width | Scales with resolution |
| Pinch gap threshold | 30% frame width | ~1.5 meters for motorcycle |
| Glare detection | Brightness > 230 | Top frame half brightness |
| Proximity critical | > 0.4 frame width | Very close vehicle |
| Reactive swerve count | > 5 for UNSAFE | Frequency-based verdict |
| Risk percentage (unsafe) | > 15% | Percentage of critical frames |
| Risk percentage (moderate) | > 5% | Threshold for caution |

---

## Output Report Example

```
DHAKA-RIDE SAFETY REPORT
========================
ANALYSIS: Optical Flow + Jerk Metric (No GPS Required)

CRITICAL EVENTS:
[Frame 145] DANGER: reactive_swerve tailgating_critical
[Frame 203] DANGER: critical_pinch_point heavy_vehicle_conflict

RIDER BEHAVIOR PROFILE
======================
STYLE: REACTIVE (High Risk)
Analysis: Rider relies on last-second swerves rather than planning ahead.

FINAL VERDICT
=============
RIDE STATUS: UNSAFE
REASON: Frequent reactive swerving detected (8 instances). Rider shows panic-based reactions.

ACTIONABLE RECOMMENDATIONS
=========================
🚨 CRITICAL ACTIONS (Do This Today)

The '3-Second Rule' Drill:
You are tailgating frequently. Practice the 'Count-to-Three' drill...

📚 DHAKA SURVIVAL TIPS (Daily Reminder)

The 'Look-Look-Go' Rule:
Before entering a main road, look Right, then Left, then Right again...
```

---

## Future Enhancements

1. **Audio Analysis**: Horn vs. brake distinction
2. **Temporal Smoothing**: Moving average for jerk (reduce noise)
3. **Trajectory Prediction**: Anticipate collision before it happens
4. **Dash-cam Integration**: Live streaming API
5. **Insurance Integration**: Premium adjustments based on verdicts
6. **Multi-Ride Analytics**: Trend detection over weeks
7. **Leaderboard**: Rider skill ranking (anonymous)
8. **AR Warnings**: In-helmet HUD overlay recommendations

---

## Files

```
g:\Capstone c\Risk Analysis\
├── video_processor.py      # Optical flow + feature detection
├── text_generator.py        # Token generation
├── risk_model.py            # Decision tree classifier
├── recommendations.py       # 23-solution recommendation engine
├── main.py                  # Main orchestration
├── test_recommendations.py  # Unit tests
├── yolov8n.pt               # YOLO model weights
└── ride_safety_report.txt   # Output report
```

---

## References

- YOLOv8: Ultralytics documentation
- Optical Flow: OpenCV Farneback algorithm
- Dhaka Traffic PDF: Safety analysis document provided
- Jerk Metric: Physics-based acceleration change detection

---

**Version**: Logic-First Rewrite (December 2025)  
**Status**: Ready for testing with real Dhaka traffic videos
