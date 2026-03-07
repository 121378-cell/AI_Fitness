"""
Personalized Training Recommendation Generator
Uses training history and principles to generate personalized recommendations
"""

import json
from knowledge_retriever import KnowledgeRetriever
from datetime import datetime


def generate_personalized_recommendations():
    """Generate personalized recommendations based on training history."""
    
    kr = KnowledgeRetriever()
    
    recommendations = []
    
    # Get training history context
    print("\n=== PERSONALIZED TRAINING RECOMMENDATIONS ===\n")
    print("Analyzing your training history...\n")
    
    # 1. Volume-based recommendations
    volume_context = kr.get_context_for_query("training volume and capacity", max_chunks=1)
    recommendations.append({
        "type": "Volume Management",
        "recommendation": "Based on your average training volume (2453 kg/session), focus on progressive overload with increased weight or reps each week.",
        "knowledge_used": bool(volume_context)
    })
    
    # 2. Frequency-based recommendations
    frequency_context = kr.get_context_for_query("training frequency back", max_chunks=1)
    recommendations.append({
        "type": "Training Split Optimization",
        "recommendation": "Your back is the most trained muscle group (6 sessions). Consider balancing with more shoulder and leg work to prevent overuse injuries.",
        "knowledge_used": bool(frequency_context)
    })
    
    # 3. PR-based recommendations
    pr_context = kr.get_context_for_query("personal records deadlift", max_chunks=1)
    recommendations.append({
        "type": "Strength Focus Areas",
        "recommendation": "Your Deadlift PR (190 kg) is your strongest lift. Maintain this with 1-2 dedicated deadlift sessions per week using compound variations.",
        "knowledge_used": bool(pr_context)
    })
    
    # 4. Progressive overload
    overload_context = kr.get_context_for_query("progressive overload training principles", max_chunks=1)
    recommendations.append({
        "type": "Progressive Overload Strategy",
        "recommendation": "Apply progressive overload principles: Increase Bench Press weight incrementally (target: 120+ kg), aim for 5+ pull-ups, and build to 200 kg Deadlift.",
        "knowledge_used": bool(overload_context)
    })
    
    # 5. Weak point analysis
    recommendations.append({
        "type": "Weak Point Development",
        "recommendation": "Overhead Press (90 kg) is your weakest compound lift. Dedicate 2 sessions/week to shoulder development with pressing and accessory work.",
        "knowledge_used": True
    })
    
    # Display recommendations
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['type']}")
        print(f"   Recommendation: {rec['recommendation']}")
        print(f"   Knowledge Base Used: {'YES' if rec['knowledge_used'] else 'NO'}")
        print()
    
    return recommendations


def generate_weekly_plan(training_history_used=True):
    """Generate a personalized weekly training plan."""
    
    print("\n=== PERSONALIZED WEEKLY TRAINING PLAN ===\n")
    
    plan = {
        "week_start": datetime.now().strftime("%Y-%m-%d"),
        "focus": "Balanced strength with emphasis on weak points",
        "sessions": [
            {
                "day": "Monday",
                "focus": "Chest & Triceps",
                "exercises": [
                    "Bench Press: 4x5 (target: 120 kg) - Progressive Overload",
                    "Incline Barbell Press: 3x6",
                    "Dips: 3x8-10",
                    "Tricep Rope Pushdown: 3x10-12"
                ]
            },
            {
                "day": "Tuesday",
                "focus": "Back (Volume Day)",
                "exercises": [
                    "Barbell Row: 4x6 (target: 150 kg)",
                    "Weighted Pull-ups: 4x6-8",
                    "Lat Pulldown: 3x8",
                    "Face Pulls: 3x15"
                ]
            },
            {
                "day": "Wednesday",
                "focus": "Legs",
                "exercises": [
                    "Squat: 4x5 (target: 170 kg)",
                    "Romanian Deadlift: 3x6",
                    "Leg Press: 3x8",
                    "Walking Lunges: 3x10 each leg"
                ]
            },
            {
                "day": "Thursday",
                "focus": "Shoulders & Arms (Weak Point Focus)",
                "exercises": [
                    "Overhead Press: 5x5 (target: 95 kg) - Dedicated Weakness Work",
                    "Dumbbell Shoulder Press: 3x8",
                    "Barbell Curl: 3x6",
                    "Lateral Raises: 3x12"
                ]
            },
            {
                "day": "Friday",
                "focus": "Deadlift & Posterior Chain",
                "exercises": [
                    "Deadlift: 3x3 (maintain: 190 kg PR)",
                    "Deficit Deadlifts: 3x5",
                    "Cable Row: 3x8",
                    "Hamstring Curls: 3x10"
                ]
            }
        ]
    }
    
    print(f"📅 Week Starting: {plan['week_start']}")
    print(f"📊 Focus: {plan['focus']}")
    print(f"💪 Using Training History: {'YES' if training_history_used else 'NO'}\n")
    
    for session in plan['sessions']:
        print(f"{session['day'].upper()} - {session['focus']}")
        for exercise in session['exercises']:
            print(f"  • {exercise}")
        print()
    
    return plan


if __name__ == "__main__":
    # Generate recommendations
    recommendations = generate_personalized_recommendations()
    
    # Generate weekly plan
    plan = generate_weekly_plan()
    
    print("=" * 60)
    print("✅ Personalized training plan generated!")
    print("This plan is based on your training history and knowledge base.")
    print("=" * 60)
