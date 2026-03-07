#!/usr/bin/env python3
"""
Garmin Data Integration Module
Reads Garmin smartwatch data and provides recovery metrics
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import json

class GarminDataProvider:
    """Load and analyze Garmin watch data"""
    
    def __init__(self, garmin_csv_path="data/garmin_stats.csv"):
        self.garmin_csv = Path(garmin_csv_path)
        self.data = None
        self.load_data()
    
    def load_data(self):
        """Load Garmin CSV with proper encoding handling"""
        if not self.garmin_csv.exists():
            print(f"[!] Garmin data not found at {self.garmin_csv}")
            self.data = pd.DataFrame()
            return
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            for encoding in encodings:
                try:
                    self.data = pd.read_csv(
                        self.garmin_csv,
                        encoding=encoding,
                        on_bad_lines='skip',
                        dtype={'Date': str}  # Keep date as string first
                    )
                    if len(self.data) > 0:
                        print(f"✓ Garmin data loaded ({len(self.data)} rows)")
                        return
                except Exception:
                    continue
            
            print(f"[!] Could not read Garmin file with any encoding")
            self.data = pd.DataFrame()
        except Exception as e:
            print(f"[!] Error loading Garmin data: {e}")
            self.data = pd.DataFrame()
    
    def parse_date(self, date_str):
        """Parse Garmin date format"""
        if pd.isna(date_str):
            return None
        try:
            return pd.to_datetime(date_str, format='%Y-%m-%d')
        except:
            try:
                return pd.to_datetime(date_str)
            except:
                return None
    
    def get_latest_metric(self, column_name, days_back=1):
        """Get latest metric from Garmin"""
        if self.data is None or len(self.data) == 0:
            return None
        
        # Parse dates
        self.data['parsed_date'] = self.data.get('Date', pd.Series()).apply(self.parse_date)
        valid_data = self.data.dropna(subset=['parsed_date'])
        
        if len(valid_data) == 0:
            return None
        
        # Sort by date and get latest
        valid_data = valid_data.sort_values('parsed_date', ascending=False)
        latest_value = valid_data[column_name].iloc[0] if column_name in valid_data.columns else None
        
        return valid_data.iloc[0] if latest_value is not None else None
    
    def get_weekly_average(self, column_name, days_back=7):
        """Get 7-day average of a metric"""
        if self.data is None or len(self.data) == 0:
            return None
        
        # Parse dates
        self.data['parsed_date'] = self.data.get('Date', pd.Series()).apply(self.parse_date)
        valid_data = self.data.dropna(subset=['parsed_date'])
        
        if len(valid_data) == 0:
            return None
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_data = valid_data[valid_data['parsed_date'] >= cutoff_date]
        
        if len(recent_data) == 0:
            return None
        
        if column_name in recent_data.columns:
            try:
                return recent_data[column_name].astype(float).mean()
            except:
                return None
        
        return None
    
    def get_recovery_score(self):
        """Calculate comprehensive recovery score (0-100)"""
        score = 50  # baseline
        factors = {}
        
        if len(self.data) == 0:
            return {"score": score, "factors": factors, "status": "NO_DATA"}
        
        # Sleep analysis
        sleep_avg = self.get_weekly_average('Sleep Total (hr)', days_back=7)
        if sleep_avg is not None:
            try:
                sleep_avg = float(sleep_avg)
                if sleep_avg >= 8:
                    factors["sleep"] = 20
                elif sleep_avg >= 7:
                    factors["sleep"] = 15
                elif sleep_avg >= 6:
                    factors["sleep"] = 10
                elif sleep_avg >= 5:
                    factors["sleep"] = 5
                else:
                    factors["sleep"] = -10
            except:
                pass
        
        # RHR (Resting Heart Rate) analysis
        rhr_avg = self.get_weekly_average('RHR', days_back=7)
        if rhr_avg is not None:
            try:
                rhr_avg = float(rhr_avg)
                if rhr_avg <= 50:
                    factors["rhr"] = 15
                elif rhr_avg <= 60:
                    factors["rhr"] = 10
                elif rhr_avg <= 70:
                    factors["rhr"] = 5
                else:
                    factors["rhr"] = -5
            except:
                pass
        
        # Activity (Steps)
        steps_avg = self.get_weekly_average('Steps', days_back=7)
        if steps_avg is not None:
            try:
                steps_avg = float(steps_avg)
                if steps_avg >= 20000:
                    factors["activity"] = 15
                elif steps_avg >= 15000:
                    factors["activity"] = 10
                elif steps_avg >= 10000:
                    factors["activity"] = 5
                elif steps_avg >= 5000:
                    factors["activity"] = 0
                else:
                    factors["activity"] = -5
            except:
                pass
        
        # HRV (if available)
        hrv_avg = self.get_weekly_average('HRV Avg', days_back=7)
        if hrv_avg is not None:
            try:
                hrv_avg = float(hrv_avg)
                if hrv_avg >= 50:
                    factors["hrv"] = 10
                elif hrv_avg >= 40:
                    factors["hrv"] = 5
                elif hrv_avg >= 30:
                    factors["hrv"] = 0
                else:
                    factors["hrv"] = -5
            except:
                pass
        
        # Calculate final score
        score = 50 + sum(factors.values())
        score = max(0, min(100, score))  # Clamp 0-100
        
        # Determine status
        if score >= 80:
            status = "EXCELLENT"
        elif score >= 60:
            status = "GOOD"
        elif score >= 40:
            status = "FAIR"
        elif score >= 20:
            status = "POOR"
        else:
            status = "CRITICAL"
        
        return {
            "score": score,
            "factors": factors,
            "status": status,
            "metrics": {
                "sleep_hours": sleep_avg,
                "rhr": rhr_avg,
                "daily_steps": steps_avg,
                "hrv": hrv_avg
            }
        }
    
    def get_latest_day_summary(self):
        """Get summary of latest day's data"""
        if len(self.data) == 0:
            return None
        
        latest = self.get_latest_metric('Date')
        if latest is None:
            return None
        
        summary = {}
        
        # Extract relevant columns
        cols_to_extract = [
            ('Date', 'date'),
            ('Sleep Total (hr)', 'sleep'),
            ('RHR', 'rhr'),
            ('Steps', 'steps'),
            ('HRV Avg', 'hrv'),
            ('Training Status', 'training_status'),
            ('Cals Total', 'calories')
        ]
        
        for col, key in cols_to_extract:
            if col in latest.index:
                summary[key] = latest[col]
        
        return summary
    
    def export_report(self, output_file="output/garmin_recovery_report.json"):
        """Export recovery analysis report"""
        recovery = self.get_recovery_score()
        latest = self.get_latest_day_summary()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "recovery_score": recovery,
            "latest_day": latest,
            "data_points": len(self.data) if self.data is not None else 0
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✓ Recovery report saved to {output_path}")
        return report

def main():
    """Test Garmin data provider"""
    provider = GarminDataProvider()
    
    print("\n" + "="*80)
    print("📊 GARMIN RECOVERY ANALYSIS")
    print("="*80)
    
    recovery = provider.get_recovery_score()
    print(f"\n🎯 Recovery Score: {recovery['score']:.0f}/100")
    print(f"Status: {recovery['status']}")
    
    print(f"\n📈 Contributing Factors:")
    for factor, value in recovery['factors'].items():
        symbol = "+" if value >= 0 else ""
        print(f"  {factor.upper()}: {symbol}{value}")
    
    print(f"\n💓 Metrics:")
    metrics = recovery['metrics']
    if metrics['sleep_hours']:
        print(f"  Sleep: {metrics['sleep_hours']:.1f}h")
    if metrics['rhr']:
        print(f"  Resting HR: {metrics['rhr']:.0f} bpm")
    if metrics['daily_steps']:
        print(f"  Steps (7-day avg): {metrics['daily_steps']:.0f}")
    if metrics['hrv']:
        print(f"  HRV: {metrics['hrv']:.0f}")
    
    latest = provider.get_latest_day_summary()
    if latest:
        print(f"\n📅 Latest Day:")
        for key, value in latest.items():
            if key != 'date':
                print(f"  {key}: {value}")
    
    provider.export_report()
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
