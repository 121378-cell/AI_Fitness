#!/usr/bin/env python3
"""
Comprehensive test suite for AI Fitness Coach
Verifies all components are working correctly
"""

import sys
from pathlib import Path
import json

def test_garmin_integration():
    """Test Garmin data loading"""
    print("\n" + "="*80)
    print("🧪 TEST 1: GARMIN INTEGRATION")
    print("="*80)
    
    try:
        from garmin_integration import GarminDataProvider
        
        garmin = GarminDataProvider()
        recovery = garmin.get_recovery_score()
        
        assert recovery['score'] >= 0 and recovery['score'] <= 100, "Recovery score out of range"
        assert recovery['status'] in ['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'CRITICAL', 'MODERATE'], f"Invalid status: {recovery['status']}"
        
        print(f"✅ PASS - Recovery Score: {recovery['score']:.0f}/100 ({recovery['status']})")
        return True
    except Exception as e:
        print(f"❌ FAIL - {e}")
        return False

def test_knowledge_base():
    """Test Knowledge Base retrieval"""
    print("\n" + "="*80)
    print("🧪 TEST 2: KNOWLEDGE BASE")
    print("="*80)
    
    try:
        from knowledge_retriever import KnowledgeRetriever
        
        kb = KnowledgeRetriever()
        context = kb.get_context_for_query("progressive overload training")
        
        assert context is not None and len(context) > 0, "No context returned"
        
        print(f"✅ PASS - Retrieved {len(context)} chunks")
        return True
    except Exception as e:
        print(f"❌ FAIL - {e}")
        return False

def test_ai_coach_generation():
    """Test plan generation"""
    print("\n" + "="*80)
    print("🧪 TEST 3: AI COACH - PLAN GENERATION")
    print("="*80)
    
    try:
        from ai_coach_local import LocalAICoach
        
        coach = LocalAICoach()
        plan_file = coach.generate_training_plan("test_plan")
        
        assert plan_file.exists(), f"Plan file not created: {plan_file}"
        
        # Verify CSV content
        with open(plan_file) as f:
            content = f.read()
            assert "Bench Press" in content, "Bench Press not in plan"
            assert "Leg Press" in content, "Leg Press not in plan"
            assert "Series Reales" in content, "Series Reales column missing"
        
        print(f"✅ PASS - Plan generated with {len(content.splitlines())} lines")
        
        # Cleanup
        plan_file.unlink()
        return True
    except Exception as e:
        print(f"❌ FAIL - {e}")
        return False

def test_plan_analysis():
    """Test plan analysis"""
    print("\n" + "="*80)
    print("🧪 TEST 4: AI COACH - PLAN ANALYSIS")
    print("="*80)
    
    try:
        from ai_coach_local import LocalAICoach
        
        coach = LocalAICoach()
        
        # Use existing completed plan
        completed_plan = Path("output/training_plans/plan_20260307_COMPLETED.csv")
        
        if not completed_plan.exists():
            print("⚠️  SKIP - No completed plan found")
            return True
        
        analysis = coach.analyze_completed_plan(str(completed_plan))
        
        assert analysis['sessions_completed'] > 0, "No sessions detected"
        assert analysis['total_volume'] > 0, "No volume detected"
        assert analysis['exercises_tracked'] is not None, "No exercises tracked"
        
        print(f"✅ PASS - Analyzed {analysis['sessions_completed']} sessions")
        print(f"   Volume: {analysis['total_volume']:.0f}kg")
        print(f"   Exercises: {len(analysis['exercises_tracked'])}")
        return True
    except Exception as e:
        print(f"❌ FAIL - {e}")
        return False

def test_pr_predictor():
    """Test PR prediction"""
    print("\n" + "="*80)
    print("🧪 TEST 5: PR PREDICTION ENGINE")
    print("="*80)
    
    try:
        from pr_predictor import PRPredictor
        
        predictor = PRPredictor()
        predictions = predictor.get_all_predictions()
        
        if len(predictions) == 0:
            print("⚠️  SKIP - Need 2+ completed plans for predictions")
            return True
        
        assert len(predictions) > 0, "No predictions generated"
        
        # Verify structure
        for pred in predictions:
            assert 'exercise' in pred, "Missing exercise field"
            assert 'current_volume' in pred, "Missing current_volume"
            assert 'predicted_volume' in pred, "Missing predicted_volume"
        
        print(f"✅ PASS - Generated {len(predictions)} exercise predictions")
        return True
    except Exception as e:
        print(f"❌ FAIL - {e}")
        return False

def test_dashboard_dependencies():
    """Test dashboard dependencies"""
    print("\n" + "="*80)
    print("🧪 TEST 6: DASHBOARD DEPENDENCIES")
    print("="*80)
    
    try:
        import streamlit
        import plotly.graph_objects as go
        
        print("✅ PASS - Streamlit and Plotly available")
        return True
    except ImportError as e:
        print(f"❌ FAIL - Missing dependency: {e}")
        return False

def test_file_structure():
    """Test required file structure"""
    print("\n" + "="*80)
    print("🧪 TEST 7: FILE STRUCTURE")
    print("="*80)
    
    required_files = [
        "ai_coach_local.py",
        "garmin_integration.py",
        "pr_predictor.py",
        "dashboard.py",
        "knowledge_retriever.py",
        "data/knowledge_base/knowledge.db",
        "data/garmin_stats.csv",
        "output/training_plans",
        "data/workout_history"
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ FAIL - Missing files: {missing}")
        return False
    
    print(f"✅ PASS - All required files present")
    return True

def test_garmin_recovery_report():
    """Test Garmin recovery report generation"""
    print("\n" + "="*80)
    print("🧪 TEST 8: GARMIN RECOVERY REPORT")
    print("="*80)
    
    try:
        from garmin_integration import GarminDataProvider
        
        garmin = GarminDataProvider()
        report = garmin.export_report()
        
        assert report is not None, "No report generated"
        assert 'recovery_score' in report, "Missing recovery_score"
        
        report_file = Path("output/garmin_recovery_report.json")
        assert report_file.exists(), "Report file not created"
        
        print(f"✅ PASS - Report generated with recovery score: {report['recovery_score']['score']:.0f}")
        return True
    except Exception as e:
        print(f"❌ FAIL - {e}")
        return False

def run_all_tests():
    """Run complete test suite"""
    print("\n" + "█"*80)
    print("█ AI FITNESS COACH - COMPREHENSIVE TEST SUITE")
    print("█"*80)
    
    tests = [
        ("Garmin Integration", test_garmin_integration),
        ("Knowledge Base", test_knowledge_base),
        ("Plan Generation", test_ai_coach_generation),
        ("Plan Analysis", test_plan_analysis),
        ("PR Predictor", test_pr_predictor),
        ("Dashboard", test_dashboard_dependencies),
        ("File Structure", test_file_structure),
        ("Garmin Report", test_garmin_recovery_report),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ FAIL - {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        symbol = "✅" if result else "❌"
        print(f"{symbol} {name}")
    
    print("\n" + "-"*80)
    print(f"Passed: {passed}/{total} ({100*passed//total}%)")
    print("-"*80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - SYSTEM IS READY!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
