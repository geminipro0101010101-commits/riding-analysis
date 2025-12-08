import sys
import os
from video_processor import VideoProcessor
from text_generator import TextGenerator
from risk_model import RiskModel
from recommendations import RecommendationEngine

def main():
    # Allow video path to be passed as command line argument or use default
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = r"G:\Capstone c\Videos\video 1.mp4"
    
    output_file = "ride_safety_report.txt"
    
    print("--- DHAKA-RIDE PROTOCOL (Logic-First) ---")
    
    # 1. Setup Processor
    processor = VideoProcessor(video_path, window_size=10)
    text_gen = TextGenerator()
    risk_ai = RiskModel()
    rec_engine = RecommendationEngine()
    risk_ai.train_mock_model() 

    print(f"\n[1/4] Processing Video: {video_path}...")
    try:
        raw_frame_data = processor.process_video()
    except Exception as e:
        print(f"Error: {e}")
        return

    if not raw_frame_data:
        print("No frames found.")
        return

    print(f"\n[2/4] Generating Dhaka-Context Descriptions...")
    try:
        descriptions = [text_gen.generate_description(f) for f in raw_frame_data]
    except Exception as e:
        print(f"Error generating descriptions: {e}")
        return
    
    if not descriptions:
        print("No descriptions generated.")
        return
    
    print("\n[3/4] Predicting Risk Levels...")
    try:
        risk_predictions = risk_ai.predict_risk(descriptions)
    except Exception as e:
        print(f"Error predicting risk: {e}")
        return

    # --- REPORTING ---
    stats = {
        'Reactive Swerves': 0,
        'Pinch Points': 0,
        'Distracted Riding': 0,
        'Heavy Vehicle Conflicts': 0,
        'Tailgating': 0,
        'Leguna Emergency Stops': 0,
        'Wrong-Way Vehicles': 0,
        'Jaywalker Crossings': 0,
        'Blind Spot Loitering': 0,
        'Red Light Violations': 0,
        'Gap Shooting': 0,
        'Speed Breaker Hits': 0,
        'Bus Blockades': 0,
        'Weaving Events': 0,
        'Slalom Maneuvers': 0,
        'Aggressive Pinch Entries': 0
    }
    
    critical_frames = 0
    safe_frames = 0
    total_samples = len(descriptions)

    try:
        with open(output_file, "w", encoding='utf-8') as f:
            f.write("DHAKA-RIDE SAFETY REPORT\n")
            f.write("========================\n")
            f.write("CRITICAL EVENTS:\n")
            f.write("-" * 40 + "\n")

            for i, (desc, risk) in enumerate(zip(descriptions, risk_predictions)):
                risk_label = risk_ai.interpret_risk(risk)
                frame_id = raw_frame_data[i]['frame_id']
                
                if risk == 2:
                    critical_frames += 1
                    f.write(f"[Frame {frame_id}] {risk_label}: {desc}\n")

                    # Track specific behaviors — prefer canonical tokens in descriptions,
                    # but also read detector flags from frame data for robustness.
                    frame = raw_frame_data[i]

                    if "reactive_swerve" in desc: stats['Reactive Swerves'] += 1
                    if "critical_pinch_point" in desc: stats['Pinch Points'] += 1
                    if "distracted_riding" in desc: stats['Distracted Riding'] += 1
                    if "heavy_vehicle_conflict" in desc: stats['Heavy Vehicle Conflicts'] += 1
                    if "tailgating_critical" in desc: stats['Tailgating'] += 1

                    # Leguna: check canonical token or legacy frame flag
                    if "CRITICAL_LEGUNA_STOP" in desc or frame.get('leguna_brake'):
                        stats['Leguna Emergency Stops'] += 1

                    # Wrong-way
                    if "WRONG_WAY_HAZARD" in desc or frame.get('wrong_way'):
                        stats['Wrong-Way Vehicles'] += 1

                    # Jaywalker / active crossing
                    if "ACTIVE_CROSSING_RISK" in desc or frame.get('jaywalker') == "ACTIVE_CROSSING_RISK":
                        stats['Jaywalker Crossings'] += 1
                    if "STATIONARY_PEDESTRIAN" in desc or frame.get('jaywalker') == "STATIONARY_PEDESTRIAN":
                        stats['Jaywalker Crossings'] += 1

                    # Blind spot
                    if "BLIND_SPOT_LOITERING" in desc or frame.get('blind_spot_loitering'):
                        stats['Blind Spot Loitering'] += 1

                    # Red light
                    if "RED_LIGHT_VIOLATION" in desc or frame.get('red_light_violation'):
                        stats['Red Light Violations'] += 1

                    # Gap shooting
                    if "AGGRESSIVE_GAP_SHOOTING" in desc or frame.get('gap_shooting'):
                        stats['Gap Shooting'] += 1

                    # Speed breaker
                    if "SPEED_BREAKER_IMPACT" in desc or frame.get('speed_breaker'):
                        stats['Speed Breaker Hits'] += 1

                    # Bus blockade
                    if "BUS_BLOCKING_LANE" in desc or frame.get('bus_blockade'):
                        stats['Bus Blockades'] += 1

                    # Weaving / slalom
                    w = frame.get('weaving')
                    if "AGGRESSIVE_WEAVING" in desc or w == True or (isinstance(w, str) and w == "AGGRESSIVE_WEAVING"):
                        stats['Weaving Events'] += 1
                    if "SLALOM_AGGRESSIVE" in desc or frame.get('slalom_aggressive'):
                        stats['Slalom Maneuvers'] += 1
                    # Track aggressive pinch entries
                    if "AGGRESSIVE_PINCH_ENTRY" in desc or frame.get('intentional_pinch_entry'):
                        stats['Aggressive Pinch Entries'] += 1
                elif risk == 0:
                    safe_frames += 1

            f.write("\n\nRIDER BEHAVIOR PROFILE\n")
            f.write("======================\n")
            
            # Behavioral assessment — Dhaka context: swerving in traffic is normal, not panic
            reactive_ratio = stats['Reactive Swerves'] / max(critical_frames, 1)
            has_heavy_traffic = stats['Heavy Vehicle Conflicts'] > 50
            
            if stats['Reactive Swerves'] > 30 and not has_heavy_traffic:
                f.write("STYLE: REACTIVE (Over-Sensitive)\n")
                f.write("Analysis: Rider reacts to minor threats excessively, even in light traffic.\n")
                f.write("Recommendation: Build confidence and trust your space awareness.\n")
            elif has_heavy_traffic and stats['Reactive Swerves'] > 10:
                f.write("STYLE: DEFENSIVE (Appropriate for Dhaka)\n")
                f.write("Analysis: Rider responds well to heavy traffic with quick reflexes.\n")
                f.write("Recommendation: Continue defensive riding. Consider anticipation techniques.\n")
            else:
                f.write("STYLE: PROACTIVE (Safe)\n")
                f.write("Analysis: Rider maintains smooth lane discipline and anticipates hazards.\n")
                f.write("Recommendation: Maintain current riding discipline.\n")

            f.write("\n\nRISK SUMMARY\n")
            f.write("============\n")
            f.write(f"Total Samples Analyzed: {total_samples}\n")
            f.write(f"Safe Frames: {safe_frames}\n")
            f.write(f"Critical Events: {critical_frames}\n\n")
            
            f.write("BREAKDOWN:\n")
            for key, val in stats.items():
                f.write(f"  {key}: {val}\n")

            # --- VERDICT LOGIC ---
            # Dhaka Context: In dense traffic, reactive swerving is expected and safe.
            # Only flag if swerves are VERY frequent (relative to critical frames) or combined with other hazards.
            risk_percentage = (critical_frames / total_samples) * 100 if total_samples > 0 else 0
            swerve_ratio = stats['Reactive Swerves'] / max(critical_frames, 1)  # % of critical frames with swerves
            
            f.write("\n\nFINAL VERDICT\n")
            f.write("=============\n")
            
            verdict = "SAFE"
            reason = "Ride demonstrates safe behavior with minimal critical risks."

            # Count aggressive pinch entries
            aggressive_pinch_count = stats.get('Aggressive Pinch Entries', 0)
            
            if stats['Distracted Riding'] > 0:
                verdict = "UNSAFE"
                reason = "Active phone distraction detected. Any phone use while riding is considered unsafe."
            elif aggressive_pinch_count > 2:  # 2+ intentional pinch entries = at least moderate
                verdict = "MODERATE RISK"
                reason = f"Multiple intentional pinch point entries detected ({aggressive_pinch_count} instances). This is aggressive riding behavior that increases collision risk."
            elif stats['Wrong-Way Vehicles'] > 5 or stats['Bus Blockades'] > 10:
                verdict = "UNSAFE"
                reason = f"High-severity hazards detected (wrong-way: {stats['Wrong-Way Vehicles']}, bus blockades: {stats['Bus Blockades']}). Immediate awareness training needed."
            elif stats['Reactive Swerves'] > 20 and swerve_ratio > 0.5:
                verdict = "UNSAFE"
                reason = f"Excessive reactive swerving ({stats['Reactive Swerves']} instances, {swerve_ratio*100:.0f}% of critical frames). Indicates poor hazard anticipation."
            elif aggressive_pinch_count > 0 and risk_percentage > 10:  # Even 1 aggressive entry + moderate risk = moderate
                verdict = "MODERATE RISK"
                reason = f"Intentional aggressive pinch point entry detected ({aggressive_pinch_count} instances) combined with other risks ({risk_percentage:.1f}% of ride). This indicates aggressive riding behavior."
            elif risk_percentage > 25:
                verdict = "UNSAFE"
                reason = f"High frequency of critical risks ({risk_percentage:.1f}% of ride). Immediate correction needed."
            elif risk_percentage > 15:
                verdict = "MODERATE RISK"
                reason = f"Occasional risky behaviors detected ({risk_percentage:.1f}% of ride). Caution and practice advised."
            elif risk_percentage > 5:
                verdict = "CAUTION"
                reason = f"Minor hazards detected ({risk_percentage:.1f}% of ride). Stay vigilant."
            else:
                verdict = "SAFE"
                reason = "Excellent defensive riding. Minimal hazards detected."

            f.write(f"RIDE STATUS: {verdict}\n")
            f.write(f"REASON: {reason}\n")

            # --- GENERATE AND APPEND RECOMMENDATIONS ---
            recommendations = rec_engine.get_recommendations(
                verdict, stats, descriptions, raw_frame_data
            )
            rec_engine.format_recommendations(recommendations, output_file)
    except IOError as e:
        print(f"Error writing to file {output_file}: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return

    print(f"\nSuccess! Report saved to {output_file}")
    print(f"Critical Events: {critical_frames} / {total_samples}")
    print(f"Reactive Swerves: {stats['Reactive Swerves']}")
    print(f"Pinch Points: {stats['Pinch Points']}")

if __name__ == "__main__":
    main()