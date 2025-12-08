class RecommendationEngine:
    """
    Generates actionable safety recommendations based on detected risks,
    verdict status, and Dhaka-specific riding patterns.
    """

    def __init__(self):
        self.universal_tips = [
            ("The 'Look-Look-Go' Rule", 
             "Before entering a main road from a side street in Dhaka, look Right, then Left, then Right again. Rickshaws often travel the wrong way."),
            
            ("CNG Cage Awareness", 
             "CNGs have a massive blind spot on their right rear due to the metal cage. Never linger near the right rear wheel of a CNG."),
            
            ("Pedestrian 'Dark Mode' Warning", 
             "Pedestrians often wear dark clothes and cross unlit highways at night. Scan the median, not just the road ahead."),
            
            ("The 'Sandwich' Exit", 
             "If you find yourself between two buses, brake and drop back. Do not accelerate to beat them unless you have 100% clear open road ahead."),
        ]

    def get_recommendations(self, verdict, stats, descriptions, raw_frame_data):
        """
        Main method: Returns list of (category, title, solution) tuples.
        """
        # Ensure stats reflect canonical detector tokens present in textual descriptions.
        # Note: main.py already counts stats for critical frames only, so we only add
        # counts for tokens that might appear in non-critical frames to ensure completeness
        token_to_stat = {
            "CRITICAL_LEGUNA_STOP": 'Leguna Emergency Stops',
            "WRONG_WAY_HAZARD": 'Wrong-Way Vehicles',
            "ACTIVE_CROSSING_RISK": 'Jaywalker Crossings',
            "STATIONARY_PEDESTRIAN": 'Jaywalker Crossings',
            "BLIND_SPOT_LOITERING": 'Blind Spot Loitering',
            "RED_LIGHT_VIOLATION": 'Red Light Violations',
            "AGGRESSIVE_GAP_SHOOTING": 'Gap Shooting',
            "SPEED_BREAKER_IMPACT": 'Speed Breaker Hits',
            "BUS_BLOCKING_LANE": 'Bus Blockades',
            "AGGRESSIVE_WEAVING": 'Weaving Events',
            "SLALOM_AGGRESSIVE": 'Slalom Maneuvers',
            "AGGRESSIVE_PINCH_ENTRY": 'Aggressive Pinch Entries'
        }

        # Only update stats if they're missing or zero (to avoid double-counting)
        # This ensures we capture events that might have been missed in main.py's critical-only counting
        for token, stat_key in token_to_stat.items():
            count = sum(1 for d in descriptions if token in d)
            if count > 0 and stats.get(stat_key, 0) == 0:
                stats[stat_key] = count
        recommendations = []

        if verdict == "UNSAFE":
            recommendations.extend(self._unsafe_recommendations(stats, descriptions))
        elif verdict == "MODERATE RISK":
            recommendations.extend(self._moderate_recommendations(stats, descriptions))
        elif verdict == "CAUTION":
            recommendations.extend(self._moderate_recommendations(stats, descriptions))
        elif verdict == "SAFE":
            recommendations.extend(self._safe_recommendations(stats, descriptions))

        # Add universal tips (always displayed)
        recommendations.extend([("General Dhaka Tips", title, tip) for title, tip in self.universal_tips])

        return recommendations

    def _unsafe_recommendations(self, stats, descriptions):
        """Category A: UNSAFE (Critical Intervention)"""
        recs = []

        # 1. Tailgating detection
        if stats.get('Tailgating', 0) > 0:
            recs.append((
                "CRITICAL",
                "The '3-Second Rule' Drill",
                "You are tailgating frequently. Practice the 'Count-to-Three' drill: Pick a landmark "
                "(like a lamp post) passed by the vehicle ahead. If you pass it before counting to three, "
                "you are too close. Increase your following distance immediately."
            ))

        # 2. Pinch point detection
        if stats.get('Pinch Points', 0) > 0:
            recs.append((
                "CRITICAL",
                "The 'Escape Route' Replay",
                "Critical Pinch Points detected. Never position yourself where you have zero escape paths. "
                "When squeezed between two large vehicles, brake and drop back—do not attempt to squeeze through."
            ))

        # Add aggressive pinch entry recommendation
        if stats.get('Aggressive Pinch Entries', 0) > 0:
            recs.append((
                "CRITICAL",
                "Intentional Pinch Point Entry - High Risk Behavior",
                f"You intentionally entered {stats.get('Aggressive Pinch Entries', 0)} pinch point(s) during this ride. "
                "This is extremely dangerous behavior. Pinch points (auto on left, divider on right) have zero escape routes. "
                "Always brake and wait for a clear path rather than forcing your way through tight spaces. "
                "This behavior significantly increases your collision risk."
            ))

        # 3. Phone distraction
        if stats.get('Distracted Riding', 0) > 0:
            recs.append((
                "CRITICAL",
                "Phone Lockout Challenge",
                "Phone use detected during riding. Enable 'Do Not Disturb While Riding' mode on your phone. "
                "Challenge: Complete your next 5 rides phone-free to reset your safety score."
            ))

        # 4. Heavy vehicle conflict
        if stats.get('Heavy Vehicle Conflicts', 0) > 0:
            recs.append((
                "CRITICAL",
                "'Leguna' Awareness Training",
                "Dhaka Context: You rode too close behind heavy vehicles (buses/trucks). In Dhaka, "
                "'Legunas' stop instantly without signaling. Increase following distance by 2x behind any public transport."
            ))

        # 5. Reactive swerves
        if stats.get('Reactive Swerves', 0) > 5:
            recs.append((
                "CRITICAL",
                "Mandatory Cooling Period",
                "Your riding style is highly reactive today. High fatigue detected. "
                "We recommend a 15-minute rest before riding again to prevent accidents."
            ))

        # 6. Glare/night riding
        glare_count = sum(1 for d in descriptions if "visibility_blindness" in d)
        if glare_count > 0:
            recs.append((
                "WARNING",
                "Glare Recovery Tips",
                "High beam glare detected. Solution: Focus your eyes on the *left white line* (or curb) "
                "of the road to maintain lane discipline without being blinded by oncoming trucks."
            ))

        # NEW: Advanced Hazard Recommendations
        if stats.get('Leguna Emergency Stops', 0) > 0:
            recs.append((
                "CRITICAL",
                "Leguna Brake Recovery Drill",
                "Legunas stop instantly without signaling. When you see a Leguna ahead with brake lights, "
                "increase distance by 20 meters immediately. Practice 'no signal' anticipation."
            ))

        if stats.get('Wrong-Way Vehicles', 0) > 0:
            recs.append((
                "CRITICAL",
                "Wrong-Way Avoidance Protocol",
                "You encountered a vehicle moving toward you in your lane. NEVER assume they'll move. "
                "Brake hard, drift right, and honk. Practice horn usage on wrong-way vehicles daily."
            ))

        if stats.get('Jaywalker Crossings', 0) > 0:
            recs.append((
                "CRITICAL",
                "Jaywalker Prediction Training",
                "Pedestrians cross without looking in Dhaka. When you see someone near the median, "
                "reduce speed by 30% and scan 3 seconds ahead. Assume every pedestrian will cross."
            ))

        if stats.get('Blind Spot Loitering', 0) > 0:
            recs.append((
                "CRITICAL",
                "Blind Spot Escape Maneuver",
                "A large vehicle is loitering in your blind spot (side edge). Brake and drop back 50 meters. "
                "Never ride alongside buses/trucks for more than 3 seconds."
            ))

        if stats.get('Red Light Violations', 0) > 0:
            recs.append((
                "CRITICAL",
                "Red Light Discipline Protocol",
                "You ran a red light while moving. In Dhaka, red lights often mean 'conflicting traffic.' "
                "Always come to a complete stop and check ALL directions before proceeding."
            ))

        if stats.get('Gap Shooting', 0) > 0:
            recs.append((
                "CRITICAL",
                "Gap Shooting Elimination Drill",
                "You aggressively cut through traffic. This is the #1 cause of motorcycle accidents in Dhaka. "
                "Practice 'patient riding': wait for clear gaps, don't create them."
            ))

        if stats.get('Speed Breaker Hits', 0) > 0:
            recs.append((
                "CRITICAL",
                "Speed Breaker Technique Mastery",
                "You hit a speed breaker without slowing. Always slow to <10 km/h before breakers. "
                "If you must swerve, check mirrors first—never swerve into oncoming traffic."
            ))

        if stats.get('Bus Blockades', 0) > 0:
            recs.append((
                "CRITICAL",
                "Bus Blockade Navigation",
                "A bus blocked your entire lane. When blocked, brake hard and wait. Do NOT squeeze under "
                "the bus or filter into the opposing lane—this causes head-on collisions."
            ))

        if stats.get('Weaving Events', 0) > 0:
            recs.append((
                "CRITICAL",
                "Lane Stability Drill",
                "Your weaving suggests poor lane control or distraction. Spend 30 minutes daily practicing "
                "smooth throttle and steering inputs. Weaving causes other riders to misjudge your path."
            ))

        if stats.get('Slalom Maneuvers', 0) > 0:
            recs.append((
                "CRITICAL",
                "Slalom Aggression Elimination",
                "You performed aggressive rapid-fire lane changes in dense traffic. This is extremely dangerous. "
                "Accept a 30-second delay rather than risk a collision. Wait for clear road sections."
            ))

        return recs

    def _moderate_recommendations(self, stats, descriptions):
        """Category B: MODERATE RISK (Skilled but Reactive)"""
        recs = []

        # 8. Smoothness score
        if stats.get('Reactive Swerves', 0) > 0:
            recs.append((
                "IMPROVEMENT",
                "The 'Smoothness' Score (Gamified)",
                "Your reflexes are good, but your planning is late. Aim for fewer reactive swerves next ride. "
                "Brake earlier and softer to reduce sudden lateral movements."
            ))

        # 9. Rickshaw prediction
        rickshaw_count = sum(1 for d in descriptions if "rickshaw_proximity" in d)
        if rickshaw_count > 0:
            recs.append((
                "AWARENESS",
                "Rickshaw Prediction Module",
                "Caution: Rickshaws in Dhaka often turn right without looking. When approaching a rickshaw "
                "from the left, always assume it will cut across your path. Hover your brake."
            ))

        # 10. Pinch point warning
        tight_filtering = sum(1 for d in descriptions if "tight_filtering" in d)
        if tight_filtering > 0:
            recs.append((
                "WARNING",
                "The 'Pinch Point' Warning",
                "You are filtering between large vehicles. In Dhaka, buses often swerve to block motorcycles. "
                "Avoid filtering if the gap is less than 1.5 meters."
            ))

        # 11. Intersection scanner
        recs.append((
            "AWARENESS",
            "Intersection Scanner",
            "Don't enter the intersection unless you can see the pavement on the other side. "
            "Always have a clear exit before entering the 'box'."
        ))

        # 12. Edge trap alert
        recs.append((
            "AWARENESS",
            "Edge Trap Alert",
            "Watch the curbs. Dhaka roads often have sand or open drains near the edge. "
            "Stay in the center-left 'tire track' of the car ahead, not the gutter."
        ))

        # 13. Late-night speed cap
        night_count = sum(1 for d in descriptions if "visibility_blindness" in d or "glare" in d)
        if night_count > 0:
            recs.append((
                "WARNING",
                "Late-Night Speed Cap",
                "Roads may be empty but hazards are invisible. At night, reduce speed by 20% "
                "to account for unlit potholes and dark pedestrians."
            ))

        # NEW: Advanced Hazard Detectors (Moderate Section)
        if stats.get('Weaving Events', 0) > 0 and stats.get('Weaving Events', 0) <= 2:
            recs.append((
                "IMPROVEMENT",
                "Lane Control Practice",
                "Minor weaving detected. Practice smooth steering inputs and throttle control on straight roads. "
                "Use the road markings as a guide for maintaining a consistent line."
            ))

        if stats.get('Gap Shooting', 0) > 0 and stats.get('Gap Shooting', 0) == 1:
            recs.append((
                "AWARENESS",
                "Gap Shooting Awareness",
                "You attempted to cut through traffic once. Recognize that small gaps close fast in Dhaka. "
                "Wait for larger, more obvious openings to move safely."
            ))

        return recs

    def _safe_recommendations(self, stats, descriptions):
        """Category C: SAFE (Proactive & Defensive)"""
        recs = []

        # 15. Safety streak badge
        if stats.get('Pinch Points', 0) == 0:
            recs.append((
                "ACHIEVEMENT",
                "Safety Streak Badge",
                "Proactive Rider Badge Earned! You successfully anticipated 100% of traffic stops today. "
                "Excellent defensive riding."
            ))

        # 17. Route optimization
        traffic_jam_safe = sum(1 for d in descriptions if "traffic_jam_safe" in d)
        if traffic_jam_safe > 0:
            recs.append((
                "OPTIMIZATION",
                "Route Optimization",
                "You handled the traffic jam safely, but spent significant time stationary. "
                "Consider alternative routes to avoid known choke points like Mogbazar Flyover."
            ))

        # 18. Defensive mentor status
        safe_gap_count = sum(1 for d in descriptions if "safe_gap" in d or "traffic_jam_safe" in d)
        if safe_gap_count > 3:
            recs.append((
                "MASTERY",
                "Defensive Mentor Status",
                "You have mastered space management. Invite a friend to 'Shadow Ride' with you "
                "to learn your proactive habits and improve their safety."
            ))

        # 19. Pothole contribution
        recs.append((
            "COMMUNITY",
            "Pothole Contribution",
            "If you encountered any hazards during this ride, tag them on the app to warn other riders. "
            "Help build a safer Dhaka community."
        ))

        return recs

    def format_recommendations(self, recommendations, output_file):
        """
        Writes formatted recommendations to the report file.
        """
        if not recommendations:
            return

        sections = {}
        for category, title, solution in recommendations:
            if category not in sections:
                sections[category] = []
            sections[category].append((title, solution))

        try:
            with open(output_file, "a", encoding='utf-8') as f:
                f.write("\n\nACTIONABLE RECOMMENDATIONS\n")
                f.write("=========================\n\n")

                # CRITICAL section first
                if "CRITICAL" in sections:
                    f.write("[!!] CRITICAL ACTIONS (Do This Today)\n")
                    f.write("-" * 40 + "\n")
                    for title, solution in sections["CRITICAL"]:
                        f.write(f"\n{title}:\n")
                        f.write(f"{solution}\n")

                # WARNING section
                if "WARNING" in sections:
                    f.write("\n\n[!] WARNING (Next Ride)\n")
                    f.write("-" * 40 + "\n")
                    for title, solution in sections["WARNING"]:
                        f.write(f"\n{title}:\n")
                        f.write(f"{solution}\n")

                # IMPROVEMENT section
                if "IMPROVEMENT" in sections:
                    f.write("\n\n[+] IMPROVEMENT TIPS (Practice These)\n")
                    f.write("-" * 40 + "\n")
                    for title, solution in sections["IMPROVEMENT"]:
                        f.write(f"\n{title}:\n")
                        f.write(f"{solution}\n")

                # AWARENESS section
                if "AWARENESS" in sections:
                    f.write("\n\n[*] AWARENESS (Learn These Patterns)\n")
                    f.write("-" * 40 + "\n")
                    for title, solution in sections["AWARENESS"]:
                        f.write(f"\n{title}:\n")
                        f.write(f"{solution}\n")

                # ACHIEVEMENT section
                if "ACHIEVEMENT" in sections:
                    f.write("\n\n[*] ACHIEVEMENT (You Nailed It!)\n")
                    f.write("-" * 40 + "\n")
                    for title, solution in sections["ACHIEVEMENT"]:
                        f.write(f"\n{title}:\n")
                        f.write(f"{solution}\n")

                # OPTIMIZATION section
                if "OPTIMIZATION" in sections:
                    f.write("\n\n[~] OPTIMIZATION (Smart Riding)\n")
                    f.write("-" * 40 + "\n")
                    for title, solution in sections["OPTIMIZATION"]:
                        f.write(f"\n{title}:\n")
                        f.write(f"{solution}\n")

                # MASTERY section
                if "MASTERY" in sections:
                    f.write("\n\n[+] MASTERY (Advanced Tips)\n")
                    f.write("-" * 40 + "\n")
                    for title, solution in sections["MASTERY"]:
                        f.write(f"\n{title}:\n")
                        f.write(f"{solution}\n")

                # COMMUNITY section
                if "COMMUNITY" in sections:
                    f.write("\n\n[&] COMMUNITY (Help Others)\n")
                    f.write("-" * 40 + "\n")
                    for title, solution in sections["COMMUNITY"]:
                        f.write(f"\n{title}:\n")
                        f.write(f"{solution}\n")

                # General tips
                if "General Dhaka Tips" in sections:
                    f.write("\n\n[?] DHAKA SURVIVAL TIPS (Daily Reminder)\n")
                    f.write("-" * 40 + "\n")
                    for title, solution in sections["General Dhaka Tips"]:
                        f.write(f"\n{title}:\n")
                        f.write(f"{solution}\n")
        except IOError as e:
            print(f"Error writing recommendations to file: {e}")
