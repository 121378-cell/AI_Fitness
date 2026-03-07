#!/usr/bin/env python3
"""
PR Prediction Engine
Predicts future personal records based on training data and progression
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
from knowledge_retriever import KnowledgeRetriever

class PRPredictor:
    """Predict Personal Records based on progressive data"""
    
    def __init__(self):
        self.analyses = self._load_analyses()
        self.kb = KnowledgeRetriever()
    
    def _load_analyses(self):
        """Load all analysis files"""
        history_dir = Path("data/workout_history")
        analyses = []
        
        if history_dir.exists():
            for json_file in sorted(history_dir.glob("*.json")):
                try:
                    with open(json_file, encoding='utf-8') as f:
                        data = json.load(f)
                        data['timestamp'] = json_file.name
                        analyses.append(data)
                except:
                    pass
        
        return analyses
    
    def get_exercise_history(self, exercise_name):
        """Get progression history for specific exercise"""
        history = []
        
        for analysis in self.analyses:
            exercises = analysis.get('based_on_previous', {}).get('exercises_tracked', [])
            
            for ex in exercises:
                if ex['name'].lower() == exercise_name.lower():
                    history.append({
                        'timestamp': analysis.get('timestamp', ''),
                        'volume': ex['total_volume'],
                        'rpe': ex['rpe_avg'],
                        'sessions': ex['sessions']
                    })
        
        return sorted(history, key=lambda x: x['timestamp'])
    
    def predict_pr(self, exercise_name, weeks_ahead=4):
        """
        Predict PR for exercise N weeks in future
        Based on:
        - Linear progression analysis
        - RPE sustainability
        - Historical patterns
        - Knowledge base principles
        """
        history = self.get_exercise_history(exercise_name)
        
        if len(history) < 2:
            return {
                "exercise": exercise_name,
                "current": None,
                "predicted": None,
                "confidence": 0,
                "reason": "Insufficient data (need at least 2 data points)"
            }
        
        # Calculate weekly progression rate
        volumes = [h['volume'] for h in history]
        rpes = [h['rpe'] for h in history]
        
        # Linear regression
        weeks = np.arange(len(volumes))
        coefficients = np.polyfit(weeks, volumes, 1)
        progression_rate = coefficients[0]  # kg/week
        
        current_volume = volumes[-1]
        current_rpe = rpes[-1]
        
        # Conservative projection (account for plateaus)
        if current_rpe >= 8.5:
            # High effort = potential plateau
            projected_volume = current_volume + (progression_rate * weeks_ahead * 0.6)
            confidence = 0.4
        elif current_rpe >= 7:
            # Moderate effort = good progression
            projected_volume = current_volume + (progression_rate * weeks_ahead * 0.8)
            confidence = 0.6
        else:
            # Low effort = room for progression
            projected_volume = current_volume + (progression_rate * weeks_ahead)
            confidence = 0.75
        
        # Ensure realistic projection
        projected_volume = max(current_volume, projected_volume)
        
        return {
            "exercise": exercise_name,
            "current_volume": current_volume,
            "current_rpe": current_rpe,
            "predicted_volume": projected_volume,
            "predicted_rpe": min(8.0, current_rpe + 0.3),  # Slight increase
            "weekly_progression": progression_rate,
            "weeks_ahead": weeks_ahead,
            "confidence": confidence,
            "data_points": len(history),
            "recommendation": self._generate_recommendation(
                exercise_name, 
                current_rpe, 
                progression_rate,
                current_volume
            )
        }
    
    def _generate_recommendation(self, exercise_name, current_rpe, progression_rate, volume):
        """Generate recommendation based on exercise analysis"""
        
        if progression_rate < 0:
            return {
                "status": "DECLINING",
                "action": "⚠️ Volume declining - check recovery and form",
                "priority": "HIGH"
            }
        elif progression_rate < 50:
            return {
                "status": "PLATEAU",
                "action": "📊 Plateau detected - consider variation or intensity increase",
                "priority": "MEDIUM"
            }
        elif progression_rate > 200:
            return {
                "status": "STRONG_PROGRESSION",
                "action": "✓ Strong progression - maintain current strategy",
                "priority": "LOW"
            }
        elif current_rpe >= 8.5:
            return {
                "status": "HIGH_EFFORT",
                "action": "🎯 Consider reducing volume or adding variation",
                "priority": "MEDIUM"
            }
        else:
            return {
                "status": "HEALTHY",
                "action": "✓ Healthy progression - continue current plan",
                "priority": "LOW"
            }
    
    def get_all_predictions(self, weeks_ahead=4):
        """Get predictions for all exercises"""
        predictions = []
        
        # Get all unique exercises
        exercises = set()
        for analysis in self.analyses:
            tracked = analysis.get('based_on_previous', {}).get('exercises_tracked', [])
            for ex in tracked:
                exercises.add(ex['name'])
        
        # Predict for each
        for exercise in sorted(exercises):
            pred = self.predict_pr(exercise, weeks_ahead)
            if pred.get('data_points', 0) >= 2:  # Only if enough data
                predictions.append(pred)
        
        return predictions
    
    def get_priority_exercises(self):
        """Identify exercises needing attention"""
        priorities = []
        
        predictions = self.get_all_predictions()
        
        for pred in predictions:
            recommendation = pred.get('recommendation', {})
            priority = recommendation.get('priority', 'LOW')
            
            if priority in ['HIGH', 'MEDIUM']:
                priorities.append({
                    'exercise': pred['exercise'],
                    'status': recommendation['status'],
                    'action': recommendation['action'],
                    'priority': priority,
                    'current_volume': pred.get('current_volume', 0),
                    'current_rpe': pred.get('current_rpe', 0)
                })
        
        return sorted(priorities, key=lambda x: {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}.get(x['priority'], 3))
    
    def export_predictions(self, output_file="output/pr_predictions.json"):
        """Export PR predictions"""
        predictions = self.get_all_predictions(weeks_ahead=4)
        priorities = self.get_priority_exercises()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "projection_weeks": 4,
            "exercises_analyzed": len(predictions),
            "predictions": predictions,
            "priority_focus": priorities,
            "top_opportunities": self._identify_top_opportunities(predictions)
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✓ Predictions saved to {output_path}")
        return report
    
    def _identify_top_opportunities(self, predictions, top_n=3):
        """Identify top 3 exercises with highest growth potential"""
        # Sort by progression rate and confidence
        sorted_preds = sorted(
            predictions,
            key=lambda x: x.get('weekly_progression', 0) * x.get('confidence', 0),
            reverse=True
        )
        
        opportunities = []
        for pred in sorted_preds[:top_n]:
            opportunities.append({
                'exercise': pred['exercise'],
                'potential_gain': pred.get('predicted_volume', 0) - pred.get('current_volume', 0),
                'weekly_rate': pred.get('weekly_progression', 0),
                'confidence': pred.get('confidence', 0)
            })
        
        return opportunities

def main():
    """Test PR predictor"""
    predictor = PRPredictor()
    
    print("\n" + "="*80)
    print("🎯 PR PREDICTION ENGINE")
    print("="*80)
    
    # Get all predictions
    predictions = predictor.get_all_predictions(weeks_ahead=4)
    
    if len(predictions) == 0:
        print("\n[!] Not enough training data for predictions yet")
        print("    Complete at least 2 training cycles to enable predictions")
        return
    
    print(f"\n📊 Analyzing {len(predictions)} exercises...")
    print("\n" + "-"*80)
    print("EXERCISE PREDICTIONS (4 weeks ahead)")
    print("-"*80)
    
    for pred in predictions:
        exercise = pred['exercise']
        current = pred.get('current_volume', 0)
        predicted = pred.get('predicted_volume', 0)
        confidence = pred.get('confidence', 0)
        
        print(f"\n{exercise}")
        print(f"  Current Volume:   {current:>8,.0f} kg")
        print(f"  Predicted (4w):   {predicted:>8,.0f} kg")
        print(f"  Projected Gain:   {predicted - current:>8,.0f} kg")
        print(f"  Confidence:       {confidence:>8.0%}")
        
        rec = pred.get('recommendation', {})
        print(f"  Status:           {rec.get('status', 'UNKNOWN')}")
        print(f"  Action:           {rec.get('action', 'N/A')}")
    
    # Priority exercises
    print("\n" + "-"*80)
    print("🎯 PRIORITY FOCUS AREAS")
    print("-"*80)
    
    priorities = predictor.get_priority_exercises()
    if priorities:
        for p in priorities:
            print(f"\n[{p['priority']}] {p['exercise']}")
            print(f"      Status: {p['status']}")
            print(f"      Action: {p['action']}")
    else:
        print("\n✓ All exercises in healthy status")
    
    # Top opportunities
    print("\n" + "-"*80)
    print("💪 TOP GROWTH OPPORTUNITIES")
    print("-"*80)
    
    predictor.export_predictions()
    
    # Read and display report
    with open("output/pr_predictions.json") as f:
        report = json.load(f)
    
    for i, opp in enumerate(report.get('top_opportunities', []), 1):
        print(f"\n{i}. {opp['exercise']}")
        print(f"   Potential Gain: {opp['potential_gain']:.0f} kg/week")
        print(f"   Confidence:     {opp['confidence']:.0%}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
