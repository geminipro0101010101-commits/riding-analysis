import cv2
import numpy as np
from ultralytics import YOLO
import os

class VideoProcessor:
    def __init__(self, video_path, window_size=10):
        self.video_path = video_path
        self.window_size = window_size
        self.model = YOLO("yolov8n.pt") 
        # Standard classes: 0=person, 1=bicycle, 2=car, 3=motorcycle, 5=bus, 7=truck, 67=cell phone
        self.relevant_classes = [0, 1, 2, 3, 5, 7, 67] 
        self.prev_flow_x = 0  # To calculate "Jerk" (Change in acceleration)
        self.blind_spot_timer = 0  # Track loitering duration in blind spots
        self.flow_x_history = []  # Track lateral flow direction reversals for weaving
        self.slalom_counter = 0  # Track aggressive weaving in dense traffic
        # Additional state for new detectors
        self.flow_history = []     # For weaving/slalom direction history
        self.prev_speed_score = 0  # For gap-shooting detection (acceleration proxy)

    def estimate_speed_proxy(self, frame, prev_gray):
        """ 
        Uses Optical Flow Magnitude as a proxy for speed.
        Returns: 'stationary', 'slow', 'fast' based on pixel shift.
        """
        if prev_gray is None:
            return 'stationary', 0, None, 0
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        # Calculate Flow Magnitude (Speed Proxy)
        magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        avg_motion = np.mean(magnitude)

        # Calculate Jerk (Sudden lateral movement) - "Reactive" behavior
        flow_x = np.mean(flow[..., 0])
        jerk_score = abs(flow_x - self.prev_flow_x)
        self.prev_flow_x = flow_x

        # Tuned thresholds: make 'slow' and 'fast' more sensitive for urban footage
        status = 'stationary'
        if avg_motion > 2.0: status = 'slow'
        if avg_motion > 15.0: status = 'fast'

        return status, jerk_score, flow, avg_motion

    def classify_dhaka_vehicle(self, label, box):
        """
        Dhaka Logic: Heuristic filter for Rickshaws & CNGs based on Aspect Ratio.
        """
        x1, y1, x2, y2 = box
        width = x2 - x1
        height = y2 - y1
        if height == 0:
            return label
        
        aspect_ratio = width / height

        # Rickshaws are wider than bicycles (passengers side-by-side or wide canopy)
        if label == 'bicycle' and aspect_ratio > 0.6:
            return 'rickshaw'
        
        # CNGs are often detected as cars but are much smaller/narrower
        if label == 'car' and width < (height * 1.1): 
            return 'cng' # Auto-rickshaw
            
        return label

    def detect_pinch_point(self, boxes, frame_width):
        """
        Calculates the 'Escape Gap' in the center of the frame.
        If gap < 30% of screen, it's a Pinch Point.
        Now also considers road dividers (edges of frame).
        """
        center_x = frame_width / 2
        left_bound = 0
        right_bound = frame_width
        
        # Check for road divider on right edge (common in Dhaka)
        # If objects are very close to right edge, treat as divider
        right_edge_threshold = frame_width * 0.95  # Within 5% of right edge
        
        for box in boxes:
            x1, y1, x2, y2 = box
            cx = (x1 + x2) / 2
            
            # Identify obstacles closing in on the center lane
            if cx < center_x:
                left_bound = max(left_bound, x2) # Obstacle on left
            else:
                # If obstacle is very close to right edge, treat as road divider
                if x1 > right_edge_threshold:
                    right_bound = frame_width  # Road divider blocks entire right side
                else:
                    right_bound = min(right_bound, x1) # Obstacle on right
        
        # Also check if rider is near right edge (likely near divider)
        # This is a heuristic: if no objects detected on right but rider is in right lane
        if len([b for b in boxes if (b[0] + b[2])/2 > center_x]) == 0:
            # No objects on right, but if we're in right lane, likely near divider
            # Conservative: assume 10% margin for road divider
            right_bound = min(right_bound, frame_width * 0.90)
                
        gap_size = right_bound - left_bound
        # 30% frame width is roughly enough space for a motorcycle
        return gap_size < (frame_width * 0.30)

    def _calculate_center_gap(self, boxes, frame_width):
        """Helper to calculate center gap size"""
        center_x = frame_width / 2
        left_bound = 0
        right_bound = frame_width
        
        for box in boxes:
            x1, y1, x2, y2 = box
            cx = (x1 + x2) / 2
            if cx < center_x:
                left_bound = max(left_bound, x2)
            else:
                right_bound = min(right_bound, x1)
        
        return right_bound - left_bound

    def detect_intentional_pinch_entry(self, boxes, prev_boxes, flow_x, frame_width):
        """
        Detects when rider intentionally enters a pinch point.
        Signs: Moving toward a narrow gap, lateral movement toward obstacles.
        """
        if not prev_boxes or len(boxes) < 2:
            return False
        
        # Calculate if gap is narrowing and rider is moving into it
        current_gap = self._calculate_center_gap(boxes, frame_width)
        prev_gap = self._calculate_center_gap(prev_boxes, frame_width)
        
        # Gap is getting smaller (rider entering pinch)
        gap_narrowing = prev_gap > current_gap and (prev_gap - current_gap) > (frame_width * 0.05)
        
        # Rider is moving laterally toward the gap (positive flow_x = moving right)
        moving_into_gap = abs(flow_x) > 1.0  # Significant lateral movement
        
        # Current gap is already small (< 40% of frame)
        already_tight = current_gap < (frame_width * 0.40)
        
        return gap_narrowing and moving_into_gap and already_tight

    def detect_leguna_brake(self, box, label, width_change_rate):
        """
        Detects Leguna (Small truck/bus) panic-braking.
        Legunas are boxy and stop instantly without signaling.
        """
        # Leguna Logic: It's detected as 'bus' or 'truck' but is physically smaller
        # In YOLO, Legunas often flicker between 'car' and 'bus'
        if label not in ['bus', 'truck', 'car']:
            return None

        box_width = box[2] - box[0]
        box_height = box[3] - box[1]
        if box_height == 0:
            return None

        aspect_ratio = box_width / box_height
        # Legunas are boxy (ratio ~0.7 to 1.2) compared to long buses
        is_leguna_shape = 0.7 < aspect_ratio < 1.2

        # If it's a Leguna AND it's "Exploding" in size (Stopping dead)
        if is_leguna_shape and width_change_rate > 0.08:
            return "CRITICAL_LEGUNA_STOP"
        return None

    def detect_wrong_way(self, box, prev_box, frame_center_x):
        """
        Detects wrong-way vehicles (rickshaws driving at you).
        Wrong-way vehicles expand and move toward center.
        """
        if prev_box is None:
            return None

        # Calculate width change
        curr_w = box[2] - box[0]
        prev_w = prev_box[2] - prev_box[0]
        # Object is getting BIGGER (Coming closer)
        expanding = curr_w > (prev_w * 1.05)

        # Object is in your lane (Center of screen) — use relative threshold
        obj_center = (box[0] + box[2]) / 2
        in_ego_lane = abs(obj_center - frame_center_x) < 200

        if expanding and in_ego_lane:
            return "WRONG_WAY_HAZARD"
        return None

    def detect_jaywalker(self, box, flow):
        """
        Detects pedestrians crossing (lateral movement in optical flow).
        Active jaywalkers have significant horizontal flow within their bbox.
        """
        # Extract optical flow ONLY within the pedestrian's box
        if flow is None:
            return "STATIONARY_PEDESTRIAN"

        x1, y1, x2, y2 = map(int, box)
        h, w = flow.shape[:2]
        x1 = max(0, min(x1, w-1))
        x2 = max(0, min(x2, w))
        y1 = max(0, min(y1, h-1))
        y2 = max(0, min(y2, h))

        if x2 <= x1 or y2 <= y1:
            return "STATIONARY_PEDESTRIAN"

        try:
            ped_flow = flow[y1:y2, x1:x2, 0]  # 0 = Horizontal Flow
            if ped_flow.size == 0:
                return "STATIONARY_PEDESTRIAN"

            avg_lateral_speed = np.mean(ped_flow)
            # Threshold: moving sideways faster than 2 pixels/frame
            if abs(avg_lateral_speed) > 2.0:
                return "ACTIVE_CROSSING_RISK"
            return "STATIONARY_PEDESTRIAN"
        except Exception:
            return "STATIONARY_PEDESTRIAN"

    def check_blind_spot_loitering(self, boxes, labels, width):
        """
        Tracks large vehicles on side edges (kill zones).
        If a large vehicle stays on the left/right edge for >30 frames, flag loitering.
        """
        large_vehicle_on_side = False

        for box, label in zip(boxes, labels):
            if label in ['bus', 'truck']:
                center = (box[0] + box[2]) / 2
                # Check if it's on the edges (not in front)
                if center < width * 0.2 or center > width * 0.8:
                    large_vehicle_on_side = True

        if large_vehicle_on_side:
            self.blind_spot_timer += 1
        else:
            self.blind_spot_timer = 0

        if self.blind_spot_timer > 30:  # 30 frames ~ 1 second (approx)
            return "BLIND_SPOT_LOITERING"
        return None

    def check_red_light(self, frame, boxes, labels, speed_status):
        """
        Detects red light violations.
        Uses HSV color detection on traffic light bbox.
        """
        for box, label in zip(boxes, labels):
            if label == 'traffic light':
                x1, y1, x2, y2 = map(int, box)

                # Safety bounds check
                h, w = frame.shape[:2]
                x1, x2 = max(0, x1), min(w, x2)
                y1, y2 = max(0, y1), min(h, y2)

                if x2 <= x1 or y2 <= y1:
                    continue

                light_img = frame[y1:y2, x1:x2]

                try:
                    hsv = cv2.cvtColor(light_img, cv2.COLOR_BGR2HSV)

                    # Red color detection (two ranges in HSV)
                    lower_red1 = np.array([0, 70, 50])
                    upper_red1 = np.array([10, 255, 255])
                    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)

                    lower_red2 = np.array([170, 70, 50])
                    upper_red2 = np.array([180, 255, 255])
                    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

                    combined_mask = cv2.bitwise_or(mask1, mask2)

                    # If red pixels > 8% of the light area AND rider is not stationary
                    red_ratio = np.sum(combined_mask) / float(light_img.size)
                    if red_ratio > 0.08:
                        if speed_status != 'stationary':
                            return "RED_LIGHT_VIOLATION"
                except Exception:
                    continue

        return None

    def detect_gap_shooting(self, ttc_status, current_speed_score, prev_speed_score):
        """
        Detects aggressive gap-shooting using TTC vs acceleration.
        If TTC is critical while rider accelerates, flag aggressive gap shooting.
        """
        # Calculate acceleration (Positive change in speed score)
        acceleration = current_speed_score - prev_speed_score

        # If the rider accelerates while the gap is critical
        # Tune: require a stronger acceleration to be considered aggressive
        if ttc_status == "critical" and acceleration > 1.0:
            return "AGGRESSIVE_GAP_SHOOTING"
        return None

    def detect_speed_breaker(self, flow):
        """
        Detects sudden vertical jolts consistent with hitting a speed breaker.
        Uses vertical optical flow (flow[...,1]) to detect camera bounce.
        """
        if flow is None:
            return None

        # Average vertical movement of the whole frame
        avg_vertical_flow = np.mean(flow[..., 1])

        # Threshold: Sudden vertical spike > 5 pixels/frame
        if abs(avg_vertical_flow) > 5.0:
            return "SPEED_BREAKER_IMPACT"
        return None

    def detect_bus_blockade(self, label, box, prev_box):
        """
        Detects a bus that is turning sideways or blocking the lane.
        If the bus gets wider but not taller, it may be turning and blocking.
        """
        if label != 'bus' or prev_box is None:
            return None

        curr_width = box[2] - box[0]
        prev_width = prev_box[2] - prev_box[0]
        # If the bus is getting wider fast (turning sideways)
        # but not getting much taller (not getting closer)
        if prev_width == 0:
            return None

        width_growth = curr_width / prev_width
        if width_growth > 1.05:  # 5% wider in one frame step
            return "BUS_BLOCKING_LANE"
        return None

    def detect_weaving(self, current_flow_x):
        """
        Detects weaving using a short history of lateral flow directions.
        Returns 'AGGRESSIVE_WEAVING' or 'STABLE_LANE'.
        """
        # 1 = Moving Right, -1 = Moving Left, 0 = Straight
        direction = 1 if current_flow_x > 2 else (-1 if current_flow_x < -2 else 0)

        self.flow_history.append(direction)
        if len(self.flow_history) > 30:  # Keep last 30 frames (~3s)
            self.flow_history.pop(0)

        # Count direction changes (zero crossings)
        changes = 0
        for i in range(1, len(self.flow_history)):
            if self.flow_history[i] != self.flow_history[i-1] and self.flow_history[i] != 0:
                changes += 1

        if changes > 5:  # Changed direction 5+ times in 3 seconds
            return "AGGRESSIVE_WEAVING"
        return "STABLE_LANE"

    def detect_slalom_aggressive(self, boxes, labels, current_flow_x, frame_width):
        """
        Detects aggressive slalom (rapid lane changing with traffic).
        Combination of gap detection + weaving + nearby traffic.
        """
        if not hasattr(self, 'slalom_counter'):
            self.slalom_counter = 0
        
        # Check if weaving
        if current_flow_x is not None:
            is_weaving = self.detect_weaving(current_flow_x)
        else:
            is_weaving = "STABLE_LANE"
        
        # Check if in dense traffic
        vehicles = [b for b, l in zip(boxes, labels) 
                    if l in ['car', 'bus', 'truck']]
        in_dense_traffic = len(vehicles) >= 3
        
        if is_weaving == "AGGRESSIVE_WEAVING" and in_dense_traffic:
            self.slalom_counter += 1
        else:
            self.slalom_counter = 0
        
        # Sustained slalom = 3+ frames of combined behavior
        return self.slalom_counter >= 3

    def process_video(self):
        # Validate video file exists
        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"Video file not found: {self.video_path}")
        
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {self.video_path}")
        
        frame_data = []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        
        if total_frames <= 0:
            cap.release()
            raise ValueError("Video file appears to be empty or invalid")
        
        # We'll sample the first and last frame of each 15-frame window (reduced from 30 for better detection)
        sampling_interval = 15
        if sampling_interval <= 0:
            sampling_interval = 15

        num_windows = total_frames // sampling_interval
        print(f"Sampling {num_windows} windows (first+last frame of each 15-frame window) with Dhaka Context Logic...")

        # previous frame object tracking for simple width-change heuristics
        prev_boxes = []
        prev_labels = []
        prev_box_sizes = []

        for i in range(num_windows):
            # Deterministic sampling: take the first and last frame in each 30-frame window
            start_frame = i * sampling_interval
            first_idx = start_frame
            last_idx = min(start_frame + sampling_interval - 1, total_frames - 1)

            # Need at least two distinct frames to compute optical flow
            if last_idx <= first_idx:
                continue

            # Read first frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(first_idx))
            ret1, frame1 = cap.read()
            if not ret1:
                break

            # Read last frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(last_idx))
            ret2, frame2 = cap.read()
            if not ret2:
                # if we couldn't read the last frame, skip this window
                continue

            # 1. Optical Flow (Speed & Jerk) + flow output for detectors
            prev_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            speed_status, jerk_score, flow, avg_motion = self.estimate_speed_proxy(frame2, prev_gray)
            flow_x = np.mean(flow[..., 0]) if flow is not None else 0
            
            # 2. Object Detection with Dhaka Logic
            results = self.model(frame2, verbose=False)[0]
            detected_objs = []
            max_proximity = 0
            has_phone = False
            current_boxes = []
            box_sizes = []

            for box in results.boxes:
                cls = int(box.cls[0])
                if cls in self.relevant_classes:
                    raw_label = self.model.names[cls]
                    coords = box.xyxy[0].tolist()
                    
                    # Apply Dhaka Classifier
                    final_label = self.classify_dhaka_vehicle(raw_label, coords)
                    
                    if cls == 67: 
                        has_phone = True
                    detected_objs.append(final_label)
                    current_boxes.append(coords)
                    
                    # Proximity Score (Width of object relative to frame)
                    curr_width = coords[2] - coords[0]
                    box_sizes.append(curr_width)
                    width_ratio = curr_width / width if width > 0 else 0
                    max_proximity = max(max_proximity, width_ratio)

            # 3. Analyze Risks
            is_pinch = self.detect_pinch_point(current_boxes, width)

            # Detect intentional aggressive pinch point entry
            intentional_pinch_entry = False
            if is_pinch and len(prev_boxes) > 0:
                intentional_pinch_entry = self.detect_intentional_pinch_entry(
                    current_boxes, prev_boxes, flow_x, width
                )

            # Simple glare check (very bright frame)
            gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            is_glare = np.mean(gray) > 230

            # Prepare detector outputs (defaults)
            leguna_flag = False
            wrong_way_flag = False
            jaywalker_state = "STATIONARY_PEDESTRIAN"
            blind_spot_flag = False
            red_light_flag = False
            gap_shoot_flag = False
            speed_breaker_flag = False
            bus_blockade_flag = False
            weaving_flag = False
            slalom_flag = False

            # TTC heuristic (very rough): if an object occupies >60% width ratio -> critical
            ttc_status = "critical" if max_proximity > 0.6 else ("warning" if max_proximity > 0.35 else "safe")

            # Gap shooting uses avg motion as a speed proxy
            current_speed_score = avg_motion

            # Loop objects for per-object detectors
            frame_center_x = width / 2
            for idx, (box, label) in enumerate(zip(current_boxes, detected_objs)):
                prev_box = prev_boxes[idx] if idx < len(prev_boxes) else None

                # width change rate for leguna/wrong-way heuristics
                curr_w = box[2] - box[0]
                prev_w = prev_box[2] - prev_box[0] if prev_box is not None else 0
                width_change_rate = (curr_w - prev_w) / prev_w if prev_w > 0 else 0

                # Leguna brake
                if self.detect_leguna_brake(box, label, width_change_rate) is not None:
                    leguna_flag = True

                # Wrong-way
                if self.detect_wrong_way(box, prev_box, frame_center_x) is not None:
                    wrong_way_flag = True

                # Jaywalker (only for person labels)
                if label in ['person']:
                    jaywalker_state = self.detect_jaywalker(box, flow)

                # Bus blockade (check first bus that satisfies condition)
                if not bus_blockade_flag and label == 'bus':
                    bus_prev = prev_boxes[idx] if idx < len(prev_boxes) else None
                    if self.detect_bus_blockade('bus', box, bus_prev) is not None:
                        bus_blockade_flag = True

            # Blind spot loitering (uses all boxes + labels)
            if self.check_blind_spot_loitering(current_boxes, detected_objs, width) is not None:
                blind_spot_flag = True

            # Red light check
            if self.check_red_light(frame2, current_boxes, detected_objs, speed_status) is not None:
                red_light_flag = True

            # Gap shooting
            if self.detect_gap_shooting(ttc_status, current_speed_score, self.prev_speed_score) is not None:
                gap_shoot_flag = True

            # Speed breaker
            if self.detect_speed_breaker(flow) is not None:
                speed_breaker_flag = True

            # Weaving detection (lateral flow)
            weaving_res = self.detect_weaving(flow_x)
            if weaving_res == "AGGRESSIVE_WEAVING":
                weaving_flag = True

            # Slalom detection (needs current labels/flow_x)
            if self.detect_slalom_aggressive(current_boxes, detected_objs, flow_x, width):
                slalom_flag = True

            # Update prev_speed_score for next frame
            self.prev_speed_score = current_speed_score

            frame_data.append({
                "frame_id": first_idx,
                "objects": detected_objs,
                "proximity": max_proximity,
                "speed": speed_status,
                "jerk": jerk_score,
                "pinch": is_pinch,
                "phone": has_phone,
                "glare": is_glare,
                # Advanced detectors
                "leguna_brake": leguna_flag,
                "wrong_way": wrong_way_flag,
                "jaywalker": jaywalker_state,
                "blind_spot_loitering": blind_spot_flag,
                "red_light_violation": red_light_flag,
                "gap_shooting": gap_shoot_flag,
                "speed_breaker": speed_breaker_flag,
                "bus_blockade": bus_blockade_flag,
                "weaving": weaving_flag,
                "slalom_aggressive": slalom_flag,
                "intentional_pinch_entry": intentional_pinch_entry
            })

            # store current as previous for next iteration (simple matching by index)
            prev_boxes = [b.copy() if hasattr(b, 'copy') else b for b in current_boxes]
            prev_labels = list(detected_objs)
            prev_box_sizes = list(box_sizes)

        cap.release()
        return frame_data