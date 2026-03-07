"""
AI Fitness Coach - Quick Reference Guide
Shows how to use the training history and knowledge base system
"""

def print_quick_guide():
    """Print a quick reference guide for the system."""
    
    guide = """
╔════════════════════════════════════════════════════════════════════════════╗
║         AI FITNESS COACH - PERSONALIZED TRAINING SYSTEM                    ║
║              Your Complete Training Knowledge Base                         ║
╚════════════════════════════════════════════════════════════════════════════╝

📊 WHAT'S NEW:
   ✅ Training History Report Generated
   ✅ Automatic Analysis of 17 Training Sessions
   ✅ Personal Records Extracted
   ✅ Training Volume Calculated
   ✅ Knowledge Base Enhanced with Personal Data

📈 YOUR TRAINING STATS:
   • Total Sessions: 17
   • Date Range: 2026-02-01 to 2026-03-05
   • Total Training Volume: 41,705 kg
   • Average Per Session: 2,453 kg
   
   Strongest Lifts:
   🥇 Deadlift: 190 kg
   🥈 Squat: 165 kg
   🥉 Barbell Row: 140 kg
   
   Most Trained:
   • Back: 6 sessions
   • Chest & Legs: 4 sessions each
   • Shoulders: 3 sessions

🧠 KNOWLEDGE BASE CONTENTS:
   📄 Document 1: Training_Principles.txt (8 chunks)
      Categories: Progressive Overload, Training Splits, Recovery
   
   📄 Document 2: training_history_report.txt (1 chunk)
      Your Personal Training History & Statistics

🎯 HOW TO USE:

   1. GENERATE PERSONALIZED RECOMMENDATIONS:
      Run: python personalized_recommendations.py
      Shows: Custom recommendations based on your training history
      
   2. UPDATE YOUR TRAINING HISTORY:
      Your training history updates automatically from hevy_stats.csv
      To regenerate report: python training_report_generator.py
      
   3. RUN THE AI FITNESS COACH:
      Run: python Gemini_Hevy.py
      The coach will use your personal training history + principles
      
   4. USE THE DASHBOARD:
      Run: python dashboard_local_server.py
      Open: http://localhost:8501
      Dashboard shows: Training history, stats, and AI recommendations
      
   5. MANAGE YOUR KNOWLEDGE BASE:
      List documents: python pdf_management.py list
      Add PDFs: python pdf_management.py add <filename>
      Search: python pdf_management.py search "topic"
      Delete: python pdf_management.py delete <id>
      Stats: python pdf_management.py stats

💡 FEATURES:

   ✨ Personalized Recommendations Based On:
      • Your training volume and capacity
      • Training frequency by muscle group
      • Your personal records and strength levels
      • Weak points identification (Overhead Press needs work!)
      • Progressive overload strategy
      
   🤖 AI Coach Integration:
      • Uses Ollama (local LLM, offline capable)
      • Enhanced with your training history
      • Generates monthly training plans
      • Provides exercise recommendations
      
   📱 Local Storage:
      • No cloud dependencies
      • All data stored locally
      • SQLite database for knowledge base
      • Historical CSV files for reference

🔧 ADDING MORE KNOWLEDGE:

   Add fitness PDFs/documents:
      python pdf_management.py add path/to/document.pdf
      
   Supported formats:
      • PDF files
      • Text files (.txt)
      • Training logs and nutrition guides
      
   Example:
      python pdf_management.py add "mobility_guide.pdf"
      python pdf_management.py add "nutrition_plan.txt"

📌 NEXT STEPS:

   1. Run personalized recommendations to see AI-generated plans
   2. Add more training PDFs (workout programs, nutrition, recovery)
   3. Use dashboard to track progress
   4. Check back in a week for updated recommendations

╔════════════════════════════════════════════════════════════════════════════╗
║                     All systems ready to use!                              ║
║              Your AI coach has access to your training history              ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
    
    print(guide)


if __name__ == "__main__":
    print_quick_guide()
