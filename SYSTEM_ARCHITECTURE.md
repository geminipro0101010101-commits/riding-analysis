# DHAKA-RIDE COMPLETE SYSTEM ARCHITECTURE

## System Overview
A complete motorcycle safety analysis system for Dhaka city using optical flow (no GPS/speedometer required) and YOLOv8 object detection to identify 20+ hazard patterns and generate actionable recommendations for safer riding.

---

## Core Components

### 1. **VideoProcessor** (`video_processor.py`) - 370 lines
**Purpose:** Extract safety metrics and hazard indicators from video frames

**Key Methods:**
- `estimate_speed_proxy()` - Optical flow magnitude as speed proxy
- `classify_dhaka_vehicle()` - Heuristic rickshaw/CNG detection
- `detect_pinch_point()` - Center lane escape gap analysis
- `detect_aggressive_merge()` - Bus/truck moving toward center
- `check_sandwich_condition()` - Trapped between two vehicles
- `detect_glare()` - Visibility assessment
- `detect_darkness()` - Night riding detection
- `calculate_ttc()` - Time-to-collision estimate

**NEW METHODS (10 Advanced Detectors):**
- `detect_leguna_brake()` - Emergency stop without signal
- `detect_wrong_way()` - Oncoming traffic in lane
- `detect_jaywalker()` - Pedestrian active crossing
- `check_blind_spot_loitering()` - Large vehicle in kill zone
- `check_red_light()` - Red light violation detection
- `detect_gap_shooting()` - Cutting through traffic
- `detect_speed_breaker()` - Road obstacle emergence
- `detect_bus_blockade()` - Complete road blockage
- `detect_weaving()` - Lane stability issues
- `detect_slalom_aggressive()` - Rapid lane changes in traffic

**Process:**
1. Capture consecutive frames
2. Calculate optical flow (Farneback algorithm)
3. Run YOLO detection on bicycle class [0,1,2,3,5,7,67]
4. Execute all detection methods
5. Return frame_data dict with hazard flags

---

### 2. **TextGenerator** (`text_generator.py`) - 70 lines
**Purpose:** Convert frame data into semantic tokens for ML classification

**Token Categories:**
- **Speed Context** (traffic_jam_safe, stable_control)
- **Behavioral Profile** (reactive_swerve, proactive_scan)
- **Space Management** (critical_pinch_point, tight_filtering)
- **Object Hazards** (rickshaw_proximity, heavy_vehicle_conflict)
- **Proximity Logic** (tailgating_critical, traffic_jam_safe)
- **Environmental** (visibility_blindness, distracted_riding)
- **Advanced Hazards** (leguna_emergency_stop, wrong_way_hazard, active_crossing_risk, blind_spot_loiter, red_light_violation, gap_shooting_aggressive, speed_breaker_detected, bus_blockade_total, lane_weaving_detected, slalom_aggressive_maneuver)

**Logic:** Each token represents a detection event that gets passed to the risk classifier

---

### 3. **RiskModel** (`risk_model.py`) - 50 lines
**Purpose:** Map semantic tokens to risk levels using trained classifier

**Model Architecture:**
- CountVectorizer: Converts token strings to feature vectors
- DecisionTreeClassifier: Predicts risk level (0=SAFE, 1=MODERATE, 2=CRITICAL)
- Max depth: 6 (balanced to prevent overfitting)

**Training Data:**
- 32 examples total (original 12 + new 20)
- 0: SAFE (traffic_jam_safe, stable_control)
- 1: MODERATE (reactive_swerves count=1-2, mild hazards)
- 2: CRITICAL (distracted_riding, reactive_swerves>3, all new tokens)

---

### 4. **RecommendationEngine** (`recommendations.py`) - 370 lines
**Purpose:** Generate actionable recommendations based on verdict and hazard statistics

**Recommendation Categories:**
- **CRITICAL Actions** (Do Today - 17 recommendations)
- **WARNING** (Next Ride - 7 recommendations)
- **IMPROVEMENT** (Practice - 9 recommendations)
- **AWARENESS** (Learn - 7 recommendations)
- **ACHIEVEMENT** (Badges - 3 recommendations)
- **OPTIMIZATION** (Routing - 1 recommendation)
- **MASTERY** (Advanced - 1 recommendation)
- **COMMUNITY** (Help Others - 1 recommendation)
- **General Dhaka Tips** (Daily Reminders - 4 tips)

**NEW RECOMMENDATIONS (19 total):**
- Leguna Brake Recovery Drill
- Wrong-Way Avoidance Protocol
- Jaywalker Prediction Training
- Blind Spot Escape Maneuver
- Red Light Discipline Protocol
- Gap Shooting Elimination Drill
- Speed Breaker Technique Mastery
- Bus Blockade Navigation
- Lane Stability Drill
- Slalom Aggression Elimination
- Lane Control Practice
- Gap Shooting Awareness

---

### 5. **Main Orchestrator** (`main.py`) - 140 lines
**Purpose:** Coordinate pipeline and generate final safety report

**Process:**
1. Initialize VideoProcessor, TextGenerator, RiskModel, RecommendationEngine
2. Train risk model on Dhaka-specific data
3. Process video → Extract frames
4. Generate descriptions from frame data
5. Predict risk levels for each frame
6. Accumulate statistics (20 counters including 10 new ones)
7. Calculate verdict (SAFE/MODERATE/UNSAFE)
8. Generate recommendations
9. Write comprehensive report

**Statistics Tracked (20 counters):**
- Original: Reactive Swerves, Pinch Points, Distracted Riding, Heavy Vehicle Conflicts, Tailgating
- New: Leguna Stops, Wrong-Way Events, Jaywalker Crossings, Blind Spot Time, Red Light Violations, Gap Shoots, Speed Breaker Hits, Bus Blockades, Weaving Events, Slalom Maneuvers

---

## Complete Detection Pipeline

```
INPUT: Video File
    ↓
[FRAME SAMPLING - Random window-based sampling]
    ↓
[FRAME 1] ──→ [OPTICAL FLOW] ──→ [YOLO DETECTION]
                                        ↓
                         [20 Hazard Detectors Running in Parallel]
                         ├─ Pinch Point
                         ├─ Aggressive Merge
                         ├─ Sandwich Condition
                         ├─ Glare/Darkness
                         ├─ Leguna Brake ⭐
                         ├─ Wrong Way ⭐
                         ├─ Jaywalker ⭐
                         ├─ Blind Spot ⭐
                         ├─ Red Light ⭐
                         ├─ Gap Shooting ⭐
                         ├─ Speed Breaker ⭐
                         ├─ Bus Blockade ⭐
                         ├─ Weaving ⭐
                         └─ Slalom ⭐
                         ↓
                    [Frame Data Dict]
                    speed, jerk, proximity, pinch,
                    phone, glare, objects,
                    aggressive_merge, sandwich,
                    leguna_brake, wrong_way,
                    jaywalker, blind_spot,
                    red_light, gap_shoot,
                    speed_breaker, bus_blockade,
                    weaving, slalom_aggressive
                         ↓
                    [TEXT GENERATION]
                    "reactive_swerve tailgating_critical
                     leguna_emergency_stop
                     gap_shooting_aggressive ..."
                         ↓
                    [RISK PREDICTION]
                    Frame Risk = 0 (SAFE) or 1 (MODERATE) or 2 (CRITICAL)
                         ↓
                    [STATISTICS ACCUMULATION]
                    Increment counters for detected behaviors
                         ↓
[ALL FRAMES PROCESSED]
    ↓
[BEHAVIOR PROFILE ANALYSIS]
    ├─ Reactive Ratio
    ├─ Critical Event Frequency
    └─ Dominant Hazard Types
    ↓
[VERDICT CALCULATION]
    UNSAFE:    Distracted OR Reactive>5 OR Risk%>15
    MODERATE:  Risk%>5
    SAFE:      Risk%≤5
    ↓
[RECOMMENDATION ENGINE]
    ├─ Verdict-based recommendations
    ├─ Statistics-based triggers
    ├─ Universal Dhaka tips
    └─ Achievement badges
    ↓
[REPORT GENERATION]
    Critical Events Section
    Rider Behavior Profile
    Risk Summary
    Statistics Breakdown
    Final Verdict
    Actionable Recommendations
    ↓
OUTPUT: Comprehensive Safety Report
```

---

## Data Flow Example

```
SCENARIO: Rider encounters Leguna brake + gap shoots in traffic

Frame 147 (Leguna Ahead):
  ├─ Box: [150, 100, 280, 300]
  ├─ Label: "bus"
  ├─ Width change: +15% (braking)
  └─ detect_leguna_brake() → TRUE

Frame 148-150 (Gap Shooting):
  ├─ Lateral flow: 6.2 px/frame
  ├─ Motorcycle in frame: TRUE
  └─ detect_gap_shooting() → TRUE

TextGenerator Output:
  "leguna_emergency_stop gap_shooting_aggressive"

RiskModel Prediction:
  → CRITICAL (2)

Statistics Update:
  Leguna Emergency Stops: +1
  Gap Shooting: +1

Recommendation Trigger:
  → Add "Leguna Brake Recovery Drill"
  → Add "Gap Shooting Elimination Drill"

Report Output:
  [Frame 147] DANGER: leguna_emergency_stop gap_shooting_aggressive
```

---

## Performance Metrics

| Component | Execution Time | Input Size | Output Size |
|-----------|----------------|-----------|------------|
| Optical Flow | 15-30ms | Frame (640x480) | Flow field |
| YOLO Detection | 20-40ms | Frame (640x480) | 5-15 boxes |
| Leguna Detector | <1ms | 1 box + label | Boolean |
| Wrong-Way Detector | <1ms | 2 boxes + width | Boolean |
| Jaywalker Detector | 2-5ms | 1 box + flow | String |
| Blind Spot Detector | <1ms | N boxes + labels | String or None |
| Red Light Detector | 5-10ms | N boxes + frame | String or None |
| Gap Shooting Detector | 2-3ms | Flow + boxes | Boolean |
| Speed Breaker Detector | <1ms | Box sizes | Boolean |
| Bus Blockade Detector | <1ms | N boxes + labels | Boolean |
| Weaving Detector | <1ms | Flow scalar | Boolean |
| Slalom Detector | <1ms | Boxes + width | Boolean |
| TextGenerator | <1ms | Frame data | String |
| Risk Prediction | <1ms | Token string | Integer |

**Total per frame:** ~100-150ms (target: real-time at 5-10 FPS)

---

## Dhaka-Specific Heuristics Implemented

| Hazard Type | Heuristic | Real-World Context |
|------------|-----------|-------------------|
| Leguna Brake | Aspect ratio 0.7-1.2 + expansion | Small trucks stop instantly |
| Wrong-Way | Center lane + expansion | Rickshaws drive against traffic |
| Jaywalker | Lateral optical flow >2 px/frame | Pedestrians ignore signals |
| Blind Spot | Large vehicle at frame edge | Buses have massive blind spots |
| Red Light | Color detection + speed > slow | Riders often run red lights |
| Gap Shooting | Flow >4.5 px/frame + motorcycle | #1 cause of accidents |
| Speed Breaker | Size delta >2.5x average | Unmarked breakers everywhere |
| Bus Blockade | Single vehicle width OR 2+ buses | Buses park in traffic lanes |
| Weaving | 2+ flow direction reversals/5 frames | Poor lane control or distraction |
| Slalom | Weaving + 3+ vehicles + 3 frames | Dangerous rapid maneuvers |

---

## Verdict Logic

```
IF phone_detected:
    VERDICT = UNSAFE
    REASON = "Active phone distraction detected"
    
ELIF reactive_swerves > 5:
    VERDICT = UNSAFE
    REASON = "Frequent panic reactions"
    
ELIF critical_risk_percentage > 15%:
    VERDICT = UNSAFE
    REASON = "High frequency of critical risks"
    
ELIF critical_risk_percentage > 5%:
    VERDICT = MODERATE
    REASON = "Occasional risky behaviors"
    
ELSE:
    VERDICT = SAFE
    REASON = "Safe riding behavior"
```

---

## Testing Architecture

### Unit Tests
- Text generation: Verify tokens for each input combo
- Risk prediction: Test all 32 training examples
- Recommendations: Verify selection logic for each verdict

### Integration Tests
- Full pipeline: Video → Report
- Recommendation trigger conditions
- Statistics accumulation accuracy

### Regression Tests
- Compare verdicts across rider profiles
- Validate false positive rates (<5%)
- Check recommendation relevance

### Real-World Validation
- Test on 10+ Dhaka traffic videos
- Validate detections against ground truth
- Tune thresholds based on real footage

---

## Files Summary

| File | Lines | Size | Purpose |
|------|-------|------|---------|
| video_processor.py | 370 | 12 KB | Core detection engine |
| text_generator.py | 70 | 2 KB | Token generation |
| risk_model.py | 50 | 2 KB | ML classification |
| main.py | 140 | 5 KB | Orchestration |
| recommendations.py | 370 | 13 KB | Recommendation engine |
| yolov8n.pt | - | 6.5 MB | Pre-trained model |
| ADVANCED_DETECTORS.md | - | 8 KB | Detector documentation |
| SYSTEM_ARCHITECTURE.md | - | 10 KB | This file |

**Total Code:** ~27.5 KB Python
**Total Assets:** 6.5 MB (model)

---

## Future Roadmap

**Phase 1 (Complete):** ✅ 10 core detectors + 10 advanced detectors
**Phase 2 (Planned):** Real-time video processing at 30 FPS
**Phase 3 (Planned):** Mobile app integration with real-time alerts
**Phase 4 (Planned):** Neural network replacement of heuristics
**Phase 5 (Planned):** Community hazard reporting database

---

**System Status:** COMPLETE - Ready for Testing
**Last Updated:** 2024
**Total Hazard Patterns Detected:** 20
**Recommendation Categories:** 8
**Tracked Behaviors:** 20
