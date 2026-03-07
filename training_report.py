"""
Training Report Generator
Generates comprehensive training reports from historical data for AI knowledge base.
"""

import os
import pandas as pd
from datetime import datetime, timedelta
import json


class TrainingReportGenerator:
    """
    Generates training reports from CSV data for the knowledge base.
    """
    
    def __init__(self, csv_path="data/hevy_stats.csv"):
        """Initialize report generator."""
        self.csv_path = csv_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load training data from CSV."""
        try:
            if os.path.exists(self.csv_path):
                self.df = pd.read_csv(self.csv_path)
                print(f"[+] Loaded {len(self.df)} training records from {self.csv_path}")
            else:
                print(f"[!] File not found: {self.csv_path}")
                self.df = pd.DataFrame()
        except Exception as e:
            print(f"Error loading CSV: {e}")
            self.df = pd.DataFrame()
    
    def analyze_training_history(self):
        """Analyze training history and generate statistics."""
        if self.df.empty:
            return {}
        
        try:
            # Convert Date to datetime
            self.df['Date'] = pd.to_datetime(self.df['Date'], format='mixed', errors='coerce')
            
            stats = {
                "total_workouts": len(self.df),
                "date_range": {
                    "start": self.df['Date'].min().strftime('%Y-%m-%d'),
                    "end": self.df['Date'].max().strftime('%Y-%m-%d')
                },
                "total_days": (self.df['Date'].max() - self.df['Date'].min()).days,
                "exercises": self.df['Exercise'].unique().tolist() if 'Exercise' in self.df.columns else [],
                "muscle_groups": self.df['MuscleGroup'].unique().tolist() if 'MuscleGroup' in self.df.columns else [],
                "volume_by_muscle": {},
                "strength_by_exercise": {},
                "training_frequency": {},
            }
            
            # Volume by muscle group
            if 'MuscleGroup' in self.df.columns and 'Weight' in self.df.columns and 'Reps' in self.df.columns:
                volume = self.df.groupby('MuscleGroup').apply(
                    lambda x: (x['Weight'] * x['Reps']).sum()
                ).to_dict()
                stats["volume_by_muscle"] = volume
            
            # Strength by exercise
            if 'Exercise' in self.df.columns and 'Weight' in self.df.columns:
                strength = self.df.groupby('Exercise')['Weight'].agg(['max', 'mean', 'count']).to_dict()
                stats["strength_by_exercise"] = {k: v for k, v in zip(
                    self.df['Exercise'].unique(),
                    self.df.groupby('Exercise')['Weight'].max().values
                )}
            
            # Training frequency
            if 'Date' in self.df.columns:
                by_week = self.df.groupby(self.df['Date'].dt.isocalendar().week).size()
                stats["avg_workouts_per_week"] = by_week.mean()
            
            return stats
        except Exception as e:
            print(f"Error analyzing data: {e}")
            return {}
    
    def generate_report(self):
        """Generate comprehensive training report."""
        if self.df.empty:
            return None
        
        stats = self.analyze_training_history()
        
        report = f"""# PERSONAL TRAINING REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## TRAINING SUMMARY
- Total Workouts: {stats.get('total_workouts', 0)}
- Training Period: {stats.get('date_range', {}).get('start', 'N/A')} to {stats.get('date_range', {}).get('end', 'N/A')}
- Duration: {stats.get('total_days', 0)} days
- Average Workouts per Week: {stats.get('avg_workouts_per_week', 0):.1f}

## EXERCISES PERFORMED ({len(stats.get('exercises', []))})
"""
        for exercise in stats.get('exercises', []):
            report += f"- {exercise}\n"
        
        report += f"\n## MUSCLE GROUPS TRAINED ({len(stats.get('muscle_groups', []))})\n"
        for muscle in stats.get('muscle_groups', []):
            report += f"- {muscle}\n"
        
        report += "\n## STRENGTH LEVELS BY EXERCISE\n"
        for exercise, max_weight in stats.get('strength_by_exercise', {}).items():
            report += f"- {exercise}: {max_weight:.1f} kg\n"
        
        report += "\n## TOTAL VOLUME BY MUSCLE GROUP\n"
        for muscle, volume in stats.get('volume_by_muscle', {}).items():
            report += f"- {muscle}: {volume:,.0f} kg\n"
        
        report += "\n## KEY ACHIEVEMENTS\n"
        report += f"- Most Trained Muscle Group: {max(stats.get('volume_by_muscle', {}), key=stats.get('volume_by_muscle', {}).get) if stats.get('volume_by_muscle') else 'N/A'}\n"
        report += f"- Strongest Exercise: {max(stats.get('strength_by_exercise', {}), key=stats.get('strength_by_exercise', {}).get) if stats.get('strength_by_exercise') else 'N/A'}\n"
        
        report += "\n## TRAINING RECOMMENDATIONS\n"
        report += "Based on your training history:\n"
        
        # Generate recommendations
        if stats.get('avg_workouts_per_week', 0) < 3:
            report += "- Increase training frequency to 3-4 times per week for better results\n"
        
        muscle_groups = stats.get('muscle_groups', [])
        if len(muscle_groups) < 4:
            report += f"- Currently training {len(muscle_groups)} muscle groups. Consider adding more variety\n"
        
        report += "- Maintain consistent weekly training schedule\n"
        report += "- Track progressive overload on key exercises\n"
        report += "- Ensure adequate recovery between sessions\n"
        
        report += f"\n---\nThis report should be used as context for AI-generated training plans.\n"
        
        return report
    
    def save_report(self, output_path="data/knowledge_base/raw_pdfs/My_Training_Report.txt"):
        """Save report to file."""
        try:
            report = self.generate_report()
            if report:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"[+] Report saved to {output_path}")
                return output_path
            else:
                print("[!] Could not generate report")
                return None
        except Exception as e:
            print(f"Error saving report: {e}")
            return None
    
    def get_report_text(self):
        """Get report as string without saving."""
        return self.generate_report()
    
    def get_statistics_summary(self):
        """Get statistics as dictionary."""
        return self.analyze_training_history()


if __name__ == "__main__":
    import sys
    
    # Default behavior: generate and save report
    generator = TrainingReportGenerator()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            # Display statistics
            stats = generator.get_statistics_summary()
            print("\n=== TRAINING STATISTICS ===")
            for key, value in stats.items():
                print(f"{key}: {value}")
        elif sys.argv[1] == "view":
            # Display report
            report = generator.get_report_text()
            if report:
                print(report)
        else:
            # Custom output path
            output_path = sys.argv[1]
            generator.save_report(output_path)
    else:
        # Default: save to standard location
        output_path = generator.save_report()
