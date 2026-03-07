"""
Training Report Generator
Analyzes training history and generates comprehensive reports
"""

import os
import pandas as pd
from datetime import datetime
from knowledge_base import KnowledgeBase
from pdf_processor import process_pdf_file


def load_training_data(csv_path="data/hevy_stats.csv"):
    """Load training data from CSV."""
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} training records")
        return df
    except Exception as e:
        print(f"Error loading training data: {e}")
        return None


def analyze_training_data(df):
    """Analyze training data and extract statistics."""
    if df is None or df.empty:
        return None
    
    analysis = {
        "total_sessions": len(df),
        "date_range": f"{df['Date'].min()} to {df['Date'].max()}",
        "exercises": df['Exercise'].unique().tolist() if 'Exercise' in df.columns else [],
        "muscle_groups": df['MuscleGroup'].unique().tolist() if 'MuscleGroup' in df.columns else [],
    }
    
    # Calculate PRs and max weights
    if 'Weight' in df.columns and 'Exercise' in df.columns:
        exercise_prs = df.groupby('Exercise')['Weight'].max().to_dict()
        analysis["exercise_prs"] = exercise_prs
    
    # Volume analysis
    if 'Weight' in df.columns and 'Reps' in df.columns and 'Sets' in df.columns:
        df['Volume'] = pd.to_numeric(df['Weight'], errors='coerce') * pd.to_numeric(df['Reps'], errors='coerce') * pd.to_numeric(df['Sets'], errors='coerce')
        analysis["total_volume"] = df['Volume'].sum()
        analysis["avg_volume_per_session"] = df['Volume'].mean()
    
    return analysis


def generate_training_report(df, analysis):
    """Generate a text report from training data."""
    report = []
    report.append("=" * 80)
    report.append("PERSONAL TRAINING HISTORY REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Overview
    report.append("TRAINING OVERVIEW")
    report.append("-" * 40)
    report.append(f"Total Training Sessions: {analysis['total_sessions']}")
    report.append(f"Date Range: {analysis['date_range']}")
    report.append("")
    
    # Exercises trained
    report.append("EXERCISES PERFORMED")
    report.append("-" * 40)
    for exc in analysis['exercises']:
        report.append(f"- {exc}")
    report.append("")
    
    # Muscle groups
    report.append("MUSCLE GROUPS TRAINED")
    report.append("-" * 40)
    for mg in analysis['muscle_groups']:
        report.append(f"- {mg}")
    report.append("")
    
    # Personal records
    if 'exercise_prs' in analysis:
        report.append("PERSONAL RECORDS (Max Weight)")
        report.append("-" * 40)
        for exercise, weight in sorted(analysis['exercise_prs'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"{exercise}: {weight} kg")
        report.append("")
    
    # Volume statistics
    if 'total_volume' in analysis:
        report.append("TRAINING VOLUME")
        report.append("-" * 40)
        report.append(f"Total Training Volume: {analysis['total_volume']:.0f} kg")
        report.append(f"Average Volume per Session: {analysis['avg_volume_per_session']:.0f} kg")
        report.append("")
    
    # Training frequency
    if 'MuscleGroup' in df.columns:
        report.append("TRAINING FREQUENCY BY MUSCLE GROUP")
        report.append("-" * 40)
        frequency = df['MuscleGroup'].value_counts().to_dict()
        for mg, count in sorted(frequency.items(), key=lambda x: x[1], reverse=True):
            report.append(f"{mg}: {count} sessions")
        report.append("")
    
    # Most trained exercises
    if 'Exercise' in df.columns:
        report.append("MOST TRAINED EXERCISES")
        report.append("-" * 40)
        exercise_freq = df['Exercise'].value_counts().head(10).to_dict()
        for exc, count in sorted(exercise_freq.items(), key=lambda x: x[1], reverse=True):
            report.append(f"{exc}: {count} times")
        report.append("")
    
    report.append("=" * 80)
    report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    
    return "\n".join(report)


def save_report_to_file(report_text, output_path="data/knowledge_base/raw_pdfs/training_history_report.txt"):
    """Save report to a text file."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"Report saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error saving report: {e}")
        return None


def add_report_to_knowledge_base(report_path):
    """Process the report and add it to the knowledge base."""
    try:
        # Process the file
        result = process_pdf_file(report_path)
        
        if result['status'] != 'success':
            print(f"Failed to process report: {result.get('error')}")
            return False
        
        # Add to knowledge base
        kb = KnowledgeBase()
        doc_id = kb.add_document(
            filename=os.path.basename(report_path),
            category="Personal Training History",
            source_path=report_path,
            extracted_file=result['file'],
            chunks=result['chunks'],
            keywords=result['keywords']
        )
        kb.close()
        
        if doc_id > 0:
            print(f"Successfully added training history to knowledge base (ID: {doc_id})")
            return True
        else:
            print("Failed to add document to knowledge base")
            return False
    except Exception as e:
        print(f"Error adding report to knowledge base: {e}")
        return False


def generate_and_add_training_report(csv_path="data/hevy_stats.csv"):
    """Main function: Generate report and add to knowledge base."""
    print("\n=== GENERATING TRAINING HISTORY REPORT ===\n")
    
    # Load data
    df = load_training_data(csv_path)
    if df is None:
        return False
    
    # Analyze
    analysis = analyze_training_data(df)
    if analysis is None:
        return False
    
    # Generate report
    report_text = generate_training_report(df, analysis)
    print("\nReport generated successfully!")
    print(report_text[:500] + "...\n")
    
    # Save to file
    report_path = save_report_to_file(report_text)
    if report_path is None:
        return False
    
    # Add to knowledge base
    success = add_report_to_knowledge_base(report_path)
    
    if success:
        print("\n=== TRAINING REPORT SUCCESSFULLY ADDED TO KNOWLEDGE BASE ===")
        print("The AI coach will now use your training history for recommendations!")
    
    return success


if __name__ == "__main__":
    generate_and_add_training_report()
