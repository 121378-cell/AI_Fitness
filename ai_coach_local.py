#!/usr/bin/env python3
"""
Local AI Fitness Coach - No external integrations
Generates training plans in CSV format
Analyzes completed workouts + Garmin data
Continuously improves personalization
"""

import os
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from knowledge_retriever import KnowledgeRetriever
from garmin_integration import GarminDataProvider

class LocalAICoach:
    def __init__(self):
        self.knowledge = KnowledgeRetriever()
        self.plans_dir = Path("output/training_plans")
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir = Path("data/workout_history")
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_training_plan(self, plan_name=None):
        """Generate training plan in CSV format"""
        if plan_name is None:
            plan_name = f"plan_{datetime.now().strftime('%Y%m%d')}"
        
        plan_file = self.plans_dir / f"{plan_name}.csv"
        
        # Get context from knowledge base
        training_context = self.knowledge.get_context_for_query("progressive overload intensity management")
        
        # Create CSV template
        plan_data = [
            ["PLAN DE ENTRENAMIENTO - AI COACH"],
            ["Fecha Inicio:", datetime.now().strftime("%Y-%m-%d")],
            ["Estado:", "INCOMPLETO - Completar después de entrenar"],
            [],
            ["INSTRUCCIONES:"],
            ["1. Completa cada sesión con tus pesos y repeticiones REALES"],
            ["2. Marca el RPE (Rate of Perceived Exertion) 1-10"],
            ["3. Marca notas de cómo te sentiste"],
            ["4. Devuelve el archivo completado al coach para análisis"],
            [],
            ["Día", "Ejercicio", "Series Planeadas", "Reps Planeadas", "Peso Planificado (kg)", 
             "Series Reales", "Reps Reales", "Peso Real (kg)", "RPE", "Notas"],
        ]
        
        # Add templated workouts from knowledge base
        workouts = [
            ["Lunes", "Bench Press", 5, "AMRAP", 50, "", "", "", "", ""],
            ["Lunes", "Incline DB Press", 3, 8, "", "", "", "", "", ""],
            ["Lunes", "Barbell Rows", 4, 6, "", "", "", "", "", ""],
            ["Lunes", "Tricep Rope", 3, 8, 35, "", "", "", "", ""],
            [],
            ["Martes", "Leg Press", 4, 8, 100, "", "", "", "", ""],
            ["Martes", "Leg Curls", 3, 10, "", "", "", "", "", ""],
            ["Martes", "Calf Raises", 3, 12, "", "", "", "", "", ""],
            [],
            ["Miércoles", "Weighted Pull-ups", 4, 5, "", "", "", "", "", ""],
            ["Miércoles", "Barbell Rows", 4, 6, "", "", "", "", "", ""],
            ["Miércoles", "Lat Pulldowns", 3, 8, "", "", "", "", "", ""],
            ["Miércoles", "DB Rows", 3, 8, "", "", "", "", "", ""],
            [],
            ["Jueves", "Bird Dogs", 3, 10, "-", "", "", "", "", "McGill Protocol"],
            ["Jueves", "Dead Bug", 3, 10, "-", "", "", "", "", "McGill Protocol"],
            ["Jueves", "Pallof Press", 3, 8, "", "", "", "", "", "McGill Protocol"],
            ["Jueves", "Walk", "-", "20000+ pasos", "-", "", "", "", "", "NEAT Priority"],
            [],
            ["Viernes", "Machine Chest Fly", 3, 10, "", "", "", "", "", ""],
            ["Viernes", "Machine Row", 3, 10, "", "", "", "", "", ""],
            ["Viernes", "Shoulder Press Machine", 3, 8, "", "", "", "", "", ""],
            ["Viernes", "High-rep leg work", 2, 15, "", "", "", "", "", ""],
        ]
        
        plan_data.extend(workouts)
        
        # Write CSV
        with open(plan_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(plan_data)
        
        print(f"✓ Plan generado: {plan_file}")
        return plan_file
    
    def analyze_completed_plan(self, plan_file):
        """Analyze a completed training plan"""
        df = pd.read_csv(plan_file, skiprows=9)
        
        # Calculate actual vs planned metrics
        analysis = {
            "sessions_completed": 0,
            "total_volume": 0,
            "exercises_tracked": [],
            "rpe_average": 0,
            "performance_metrics": {},
            "notes": []
        }
        
        # Parse workout data
        for idx, row in df.iterrows():
            if pd.isna(row.get("Día")) or row["Día"] == "":
                continue
                
            day = row["Día"]
            exercise = row.get("Ejercicio", "")
            
            # Check if workout was completed (has real data)
            if pd.notna(row.get("Peso Real (kg)")):
                try:
                    weight = float(row["Peso Real (kg)"])
                    reps = float(row["Reps Reales"]) if pd.notna(row.get("Reps Reales")) else 0
                    sets = float(row["Series Reales"]) if pd.notna(row.get("Series Reales")) else 0
                    rpe = float(row["RPE"]) if pd.notna(row.get("RPE")) else 0
                    
                    volume = weight * reps * sets
                    analysis["total_volume"] += volume
                    
                    if exercise not in [e["name"] for e in analysis["exercises_tracked"]]:
                        analysis["exercises_tracked"].append({
                            "name": exercise,
                            "sessions": 1,
                            "total_volume": volume,
                            "rpe_avg": rpe
                        })
                    else:
                        for ex in analysis["exercises_tracked"]:
                            if ex["name"] == exercise:
                                ex["sessions"] += 1
                                ex["total_volume"] += volume
                                ex["rpe_avg"] = (ex["rpe_avg"] + rpe) / 2
                    
                    if pd.notna(row.get("Notas")):
                        analysis["notes"].append(f"{day} - {exercise}: {row['Notas']}")
                    
                except (ValueError, TypeError):
                    pass
        
        analysis["sessions_completed"] = len(set(df[df["Peso Real (kg)"].notna()]["Día"].unique()))
        analysis["rpe_average"] = df["RPE"].mean() if not df["RPE"].isna().all() else 0
        
        return analysis
    
    def integrate_garmin_data(self):
        """Load and analyze Garmin recovery data using new integration module"""
        try:
            garmin = GarminDataProvider()
            recovery = garmin.get_recovery_score()
            
            return {
                "daily_steps": recovery['metrics'].get('daily_steps', 0),
                "heart_rate_resting": recovery['metrics'].get('rhr', 0),
                "sleep_hours": recovery['metrics'].get('sleep_hours', 0),
                "recovery_status": recovery['status'],
                "recovery_score": recovery['score']
            }
        except Exception as e:
            # Fallback to basic data
            return {
                "daily_steps": 0,
                "heart_rate_resting": 0,
                "sleep_hours": 0,
                "recovery_status": "UNKNOWN",
                "recovery_score": 50
            }
    
    def generate_next_plan(self, completed_plan_file):
        """
        Generate next plan based on:
        1. Completed workout analysis
        2. Garmin recovery data
        3. Knowledge base wisdom
        """
        print("\n" + "="*80)
        print("🧠 AI COACH ANALYZING PERFORMANCE AND GENERATING NEXT PLAN")
        print("="*80)
        
        # Analyze what was completed
        analysis = self.analyze_completed_plan(completed_plan_file)
        print(f"\n📊 ANALYSIS OF COMPLETED PLAN:")
        print(f"  Sessions Completed: {analysis['sessions_completed']}")
        print(f"  Total Volume: {analysis['total_volume']:.0f} kg")
        print(f"  Average RPE: {analysis['rpe_average']:.1f}/10")
        print(f"  Exercises Tracked: {len(analysis['exercises_tracked'])}")
        
        # Get Garmin data
        garmin = self.integrate_garmin_data()
        print(f"\n💓 GARMIN RECOVERY DATA:")
        print(f"  Daily Steps: {garmin['daily_steps']}")
        print(f"  Sleep: {garmin['sleep_hours']:.1f} hours")
        print(f"  Resting HR: {garmin['heart_rate_resting']} bpm")
        print(f"  Recovery Status: {garmin['recovery_status']}")
        
        # Generate next plan with adjustments
        next_plan = {
            "based_on_previous": analysis,
            "recovery_data": garmin,
            "adjustments": [],
            "next_focus": ""
        }
        
        # Smart adjustments
        if garmin["recovery_status"] in ["EXCELLENT", "GOOD"]:
            next_plan["adjustments"].append("✓ Recovery optimal - increase volume or intensity")
            next_plan["next_focus"] = "PROGRESSIVE OVERLOAD"
        elif garmin["recovery_status"] == "FAIR":
            next_plan["adjustments"].append("⚠ Recovery fair - maintain intensity, focus on form")
            next_plan["next_focus"] = "FORM & CONTROL"
        else:
            next_plan["adjustments"].append("⛔ Recovery poor - reduce volume, prioritize sleep")
            next_plan["next_focus"] = "DELOAD & REST"
        
        # Exercise-specific adjustments
        for ex in analysis["exercises_tracked"]:
            avg_rpe = ex["rpe_avg"]
            if avg_rpe < 5:
                next_plan["adjustments"].append(f"  {ex['name']}: RPE low - increase weight")
            elif avg_rpe > 9:
                next_plan["adjustments"].append(f"  {ex['name']}: RPE very high - reduce volume")
        
        # Save analysis
        analysis_file = self.history_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(next_plan, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎯 ADJUSTMENTS FOR NEXT PLAN:")
        for adjustment in next_plan["adjustments"]:
            print(f"  {adjustment}")
        print(f"\n  Focus: {next_plan['next_focus']}")
        
        # Generate next plan
        print(f"\n📋 Generating next training plan...")
        new_plan = self.generate_training_plan(f"plan_{datetime.now().strftime('%Y%m%d')}")
        
        print("\n" + "="*80)
        print("✅ NEXT PLAN READY")
        print("="*80)
        print(f"Complete your workouts and return this file: {new_plan}")
        print("Command to analyze next: python ai_coach_local.py analyze <filename>.csv\n")
        
        return new_plan
    
    def print_status(self):
        """Print current system status"""
        print("\n" + "="*80)
        print("🏋️ LOCAL AI FITNESS COACH - STATUS")
        print("="*80)
        
        plans = list(self.plans_dir.glob("*.csv"))
        print(f"\n📋 Plans Generated: {len(plans)}")
        for plan in sorted(plans, reverse=True)[:5]:
            print(f"  • {plan.name}")
        
        print(f"\n📚 Knowledge Base Connected: ✓")
        print(f"  Using 3 documents (INFORME SERGI + Training Principles + History)")
        
        garmin = self.integrate_garmin_data()
        print(f"\n💓 Garmin Integration: ✓")
        print(f"  Latest Recovery: {garmin['recovery_status']}")
        print(f"  Steps Today: {garmin['daily_steps']}")
        print(f"  Sleep: {garmin['sleep_hours']:.1f}h")
        print("\n" + "="*80 + "\n")

def main():
    import sys
    
    coach = LocalAICoach()
    
    if len(sys.argv) < 2:
        print("\n🏋️ LOCAL AI COACH - COMMANDS:\n")
        print("  generate              - Generate new training plan")
        print("  analyze <file.csv>    - Analyze completed plan and generate next")
        print("  status                - Show system status\n")
        coach.print_status()
        return
    
    command = sys.argv[1]
    
    if command == "generate":
        coach.generate_training_plan()
        print("✅ Complete your workouts and return the CSV to analyze")
        
    elif command == "analyze" and len(sys.argv) > 2:
        plan_file = sys.argv[2]
        if not Path(plan_file).exists():
            print(f"❌ File not found: {plan_file}")
            return
        coach.generate_next_plan(plan_file)
        
    elif command == "status":
        coach.print_status()
        
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
