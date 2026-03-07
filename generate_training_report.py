"""
Integration script to generate training report and add it to knowledge base
"""

import os
import sys
from training_report import TrainingReportGenerator
import subprocess


def generate_and_integrate_report():
    """Generate training report and integrate into knowledge base."""
    print("[*] Generating your personal training report...")
    print("-" * 50)
    
    # Generate report
    generator = TrainingReportGenerator()
    stats = generator.get_statistics_summary()
    
    if not stats:
        print("[!] No training data found. Please ensure hevy_stats.csv has data.")
        return False
    
    # Save report
    report_path = generator.save_report()
    if not report_path:
        print("[!] Failed to generate report")
        return False
    
    print("\n[+] Report generated successfully!")
    print("\n[SUMMARY STATISTICS]")
    print(f"   - Total Workouts: {stats.get('total_workouts', 0)}")
    print(f"   - Training Period: {stats.get('date_range', {}).get('start', 'N/A')} to {stats.get('date_range', {}).get('end', 'N/A')}")
    print(f"   - Avg Workouts/Week: {stats.get('avg_workouts_per_week', 0):.1f}")
    print(f"   - Exercises: {len(stats.get('exercises', []))}")
    print(f"   - Muscle Groups: {len(stats.get('muscle_groups', []))}")
    
    # Add to knowledge base
    print("\n[*] Adding to Knowledge Base...")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, "pdf_management.py", "add", report_path, "--category", "Training History"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print("\n[SUCCESS] Your training report has been added to the knowledge base.")
            print("\n[INFO] The AI coach will now use your complete training history")
            print("       to generate personalized plans.\n")
            return True
        else:
            print(f"[!] Error adding to knowledge base:")
            print(result.stderr)
            print("\n⚠️  But your report file was created at:")
            print(f"   {report_path}")
            return False
    
    except subprocess.TimeoutExpired:
        print("[!] Timeout adding to knowledge base")
        return False
    except Exception as e:
        print(f"[!] Error: {e}")
        return False


def display_report():
    """Display the generated report."""
    generator = TrainingReportGenerator()
    report = generator.get_report_text()
    if report:
        print(report)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "view":
        display_report()
    else:
        success = generate_and_integrate_report()
        
        if success:
            print("=" * 50)
            print("[NEXT STEPS]")
            print("=" * 50)
            print("1. View your report:")
            print("   python generate_training_report.py view")
            print("\n2. Generate a new training plan:")
            print("   python Gemini_Hevy.py")
            print("\n3. The AI will use your complete training history!")
