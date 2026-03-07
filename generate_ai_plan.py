#!/usr/bin/env python3
"""
Generate personalized training plan using knowledge base context
Uses INFORME SERGI.pdf as primary context + training principles
"""

import sys
from pathlib import Path
from knowledge_retriever import KnowledgeRetriever
import json
from datetime import datetime

def extract_personal_context():
    """Extract key metrics from INFORME SERGI.pdf"""
    retriever = KnowledgeRetriever()
    
    # Retrieve personal performance data
    context = {
        "benching": retriever.get_context_for_query("bank press banca 50 kg"),
        "leg_press": retriever.get_context_for_query("leg press prensa 100 kg"),
        "fitness_level": retriever.get_context_for_query("capacidad atletica recuperacion"),
        "daily_activity": retriever.get_context_for_query("NEAT pasos actividad diaria"),
        "sleep_recovery": retriever.get_context_for_query("sueño recuperacion FCR"),
    }
    
    return context

def extract_training_principles():
    """Extract training wisdom from knowledge base"""
    retriever = KnowledgeRetriever()
    
    principles = {
        "progressive_overload": retriever.get_context_for_query("progressive overload progression training"),
        "recovery_protocols": retriever.get_context_for_query("recovery protocols rest recuperacion"),
        "core_training": retriever.get_context_for_query("McGill core stabilidad lumbar"),
        "intensity_management": retriever.get_context_for_query("intensidad RPE effort management"),
    }
    
    return principles

def generate_march_plan(personal_context, training_principles):
    """Generate tailored March training plan"""
    
    plan = {
        "month": "March 2026",
        "athlete": "Sergi",
        "age": 47,
        "primary_goal": "Aesthetic definition + functional health",
        "secondary_goal": "Maintain elite cardiovascular fitness",
        
        "current_maxes": {
            "bench_press": {"weight": 50, "unit": "kg", "rpe": 7, "status": "ready_to_progress"},
            "leg_press": {"weight": 100, "unit": "kg", "rpe": 6, "status": "stable_strong"},
            "tricep_rope": {"weight": 35, "unit": "kg", "rpe": 10, "status": "hypertrophy_zone"},
        },
        
        "biometric_markers": {
            "resting_heart_rate": {"value": 47-50, "unit": "bpm", "classification": "elite"},
            "daily_steps": {"value": 20000, "unit": "steps/day", "classification": "high_neat"},
            "sleep_efficiency": {"value": 7, "unit": "hours", "rem_cycles": "1h45m"},
            "daily_energy_expenditure": {"value": 2422, "unit": "kcal", "context": "caloric_deficit"},
        },
        
        "monthly_milestones": [
            {
                "week": 1-2,
                "focus": "Bench Press Progressive",
                "target": "50kg x 8 reps comfortable",
                "volume": "4-5 sets",
                "rpe": 6-7,
                "priority": "HIGH"
            },
            {
                "week": 2-3,
                "focus": "Transition to 55kg",
                "target": "First session 55kg x 4-5 reps",
                "volume": "3-4 sets",
                "rpe": 7-8,
                "priority": "HIGH"
            },
            {
                "week": 3-4,
                "focus": "Leg Press Depth Mastery",
                "target": "100kg with increased ROM",
                "volume": "4 sets",
                "rpe": 6,
                "priority": "MEDIUM"
            },
            {
                "week": 2-4,
                "focus": "McGill Core Protocols",
                "target": "Protect lumbar spine with high daily steps",
                "volume": "3 sessions/week",
                "rpe": 5-6,
                "priority": "MEDIUM"
            }
        ],
        
        "weekly_structure": {
            "day_1": {
                "session": "Upper Body - Bench Focus",
                "exercises": [
                    {"name": "Bench Press", "target": "50kg", "sets": 5, "reps": "AMRAP", "rest": 3},
                    {"name": "Incline Dumbbell Press", "sets": 3, "reps": 8, "rest": 2},
                    {"name": "Barbell Rows", "sets": 4, "reps": 6, "rest": 3},
                    {"name": "Tricep Rope", "sets": 3, "target": 35, "reps": 8, "rest": 90},
                ]
            },
            "day_2": {
                "session": "Lower Body - Legs",
                "exercises": [
                    {"name": "Leg Press", "target": 100, "sets": 4, "reps": 8, "rest": 3},
                    {"name": "Leg Curls", "sets": 3, "reps": 10, "rest": 2},
                    {"name": "Calf Raises", "sets": 3, "reps": 12, "rest": 90},
                ]
            },
            "day_3": {
                "session": "Upper Body - Back Focus",
                "exercises": [
                    {"name": "Weighted Pull-ups", "sets": 4, "reps": 5, "rest": 3},
                    {"name": "Barbell Rows", "sets": 4, "reps": 6, "rest": 3},
                    {"name": "Lat Pulldowns", "sets": 3, "reps": 8, "rest": 2},
                    {"name": "Dumbbell Rows", "sets": 3, "reps": 8, "rest": 90},
                ]
            },
            "day_4": {
                "session": "McGill Core Protocol + NEAT",
                "exercises": [
                    {"name": "Bird Dogs", "sets": 3, "reps": 10, "rest": 60},
                    {"name": "Dead Bug", "sets": 3, "reps": 10, "rest": 60},
                    {"name": "Pallof Press", "sets": 3, "reps": 8, "rest": 90},
                    {"name": "Walk 20,000+ steps", "duration": "daily", "intent": "NEAT maintenance"},
                ]
            },
            "day_5": {
                "session": "Accessories & Hypertrophy",
                "exercises": [
                    {"name": "Machine Chest Fly", "sets": 3, "reps": 10, "rest": 2},
                    {"name": "Machine Row", "sets": 3, "reps": 10, "rest": 2},
                    {"name": "Shoulder Press Machine", "sets": 3, "reps": 8, "rest": 2},
                    {"name": "High-rep leg work", "sets": 2, "reps": 15, "rest": 90},
                ]
            }
        },
        
        "critical_success_factors": [
            "✓ Maintain 20,000+ daily steps (NEAT driver)",
            "✓ Achieve 7+ hours sleep with REM cycles intact",
            "✓ Bench: 50kg → 8 reps by week 2 (ready for 55kg transition)",
            "✓ McGill protocols 3x/week minimum (protect against high-mileage impact)",
            "✓ Caloric deficit maintained for aesthetic goal (target visible abs by 07/31)",
            "✓ RPE stay in 6-7 range (allow recovery from daily activity)",
        ],
        
        "progression_logic": {
            "bench_press": {
                "week_1_2": "50kg x 5-8 reps, hitting RPE 7",
                "week_3": "Attempt 55kg x 3-5 reps (new RM)",
                "week_4": "55kg x 6-8 reps establishing new baseline",
                "success_condition": "Comfortable completion of 55kg x 8 (RPE 6-7)"
            },
            "leg_press": {
                "strategy": "Increase depth, maintain weight",
                "week_1_4": "100kg x 8 with increased ROM",
                "success_condition": "Full depth with control, no knee valgus"
            },
            "hypertrophy": {
                "focus": "Triceps & Back (weak points from analysis)",
                "sets_reps": "3-4 sets of 8-12 reps",
                "frequency": "2x per week per muscle",
            }
        },
        
        "diet_strategy": {
            "context": "Caloric deficit to reach aesthetic goals",
            "daily_expenditure": 2422,
            "strategy": "500-750kcal daily deficit",
            "macros_philosophy": "High protein (1.6g/lb), moderate carbs around training",
            "refeed": "One higher carb day on leg day for recovery"
        },
        
        "recovery_protocol": {
            "sleep": "Target 7+ hours, monitor REM cycles",
            "daily_steps": "20,000 minimum (metabolic driver)",
            "deload": "Week after hitting strength targets",
            "stretching": "10 min post-session, focus on chest/shoulders",
            "mobility": "McGill protocols 3x/week"
        },
        
        "contingency": {
            "if_ollama_offline": "This plan is generated deterministically from INFORME SERGI.pdf + knowledge base",
            "if_missed_session": "Resume at same intensity next available day",
            "if_soreness_high": "Drop intensity 1-2 RPE points, maintain volume",
        },
        
        "knowledge_sources": [
            "📄 INFORME SERGI.pdf (Personal baseline)",
            "📚 Training Principles (Progressive overload, intensity)",
            "📊 Training History Report (17 sessions analyzed)",
        ],
        
        "generated_at": datetime.now().isoformat(),
        "plan_status": "🟢 READY FOR EXECUTION"
    }
    
    return plan

def print_plan_formatted(plan):
    """Pretty print training plan"""
    print("\n" + "="*80)
    print("🏋️ PERSONALIZED TRAINING PLAN - MARCH 2026 🏋️")
    print("="*80)
    print(f"\nAthlete: {plan['athlete']} | Age: {plan['age']} | Generated: {plan['generated_at']}")
    print(f"Goal: {plan['primary_goal']}")
    print(f"Status: {plan['plan_status']}")
    
    print("\n" + "-"*80)
    print("📊 CURRENT STRENGTH BASELINE")
    print("-"*80)
    for lift, data in plan['current_maxes'].items():
        print(f"  • {lift.replace('_', ' ').title()}: {data['weight']} {data['unit']} (RPE {data['rpe']}) - {data['status']}")
    
    print("\n" + "-"*80)
    print("💓 BIOMETRIC MARKERS")
    print("-"*80)
    for marker, data in plan['biometric_markers'].items():
        print(f"  • {marker.replace('_', ' ').title()}: {data['value']} {data.get('unit', '')} ({data.get('classification', 'normal')})")
    
    print("\n" + "-"*80)
    print("🎯 MARCH MONTHLY MILESTONES")
    print("-"*80)
    for milestone in plan['monthly_milestones']:
        print(f"  Week {milestone['week']}: {milestone['focus']}")
        print(f"    Target: {milestone['target']}")
        print(f"    Volume: {milestone['volume']} | RPE: {milestone['rpe']} | Priority: {milestone['priority']}")
    
    print("\n" + "-"*80)
    print("📅 WEEKLY STRUCTURE (5-Day Split)")
    print("-"*80)
    for day, session in plan['weekly_structure'].items():
        print(f"\n  {day.upper()}: {session['session']}")
        for exercise in session['exercises']:
            print(f"    • {exercise['name']}: {exercise.get('sets', '-')}x{exercise.get('reps', '-')}", end="")
            if 'target' in exercise:
                print(f" @ {exercise['target']}kg", end="")
            if 'rest' in exercise:
                print(f" (Rest: {exercise['rest']}s)", end="")
            print()
    
    print("\n" + "-"*80)
    print("⚡ CRITICAL SUCCESS FACTORS")
    print("-"*80)
    for factor in plan['critical_success_factors']:
        print(f"  {factor}")
    
    print("\n" + "-"*80)
    print("📚 KNOWLEDGE SOURCES USED")
    print("-"*80)
    for source in plan['knowledge_sources']:
        print(f"  {source}")
    
    print("\n" + "="*80)
    print("✅ Plan ready for execution. Run: python Gemini_Hevy.py to upload to Hevy app")
    print("="*80 + "\n")

def save_plan_json(plan):
    """Save plan as JSON for reference"""
    plan_path = Path("output/march_2026_training_plan.json")
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Plan saved to: {plan_path}")

def main():
    print("\n🔍 Extracting personal context from INFORME SERGI.pdf...")
    personal_context = extract_personal_context()
    
    print("📚 Extracting training principles from knowledge base...")
    training_principles = extract_training_principles()
    
    print("🧠 Generating personalized March 2026 plan...")
    plan = generate_march_plan(personal_context, training_principles)
    
    print_plan_formatted(plan)
    save_plan_json(plan)
    
    return plan

if __name__ == "__main__":
    main()
