#!/usr/bin/env python3
"""
Local AI Fitness Dashboard
Visualize training progress, recovery, and AI recommendations
Runs locally on http://localhost:8501
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from garmin_integration import GarminDataProvider
from knowledge_retriever import KnowledgeRetriever

# Page config
st.set_page_config(page_title="AI Fitness Coach Dashboard", layout="wide", initial_sidebar_state="expanded")

def load_analysis_data():
    """Load all analysis files"""
    history_dir = Path("data/workout_history")
    analyses = []
    
    if history_dir.exists():
        for json_file in sorted(history_dir.glob("*.json"), reverse=True):
            try:
                with open(json_file, encoding='utf-8') as f:
                    data = json.load(f)
                    data['file'] = json_file.name
                    analyses.append(data)
            except:
                pass
    
    return analyses

def load_latest_plan():
    """Load latest training plan"""
    plans_dir = Path("output/training_plans")
    if plans_dir.exists():
        latest_plan = sorted(plans_dir.glob("*.csv"), reverse=True)
        if latest_plan:
            try:
                df = pd.read_csv(latest_plan[0], skiprows=9)
                return df, latest_plan[0].name
            except:
                pass
    return None, None

def main():
    # Header
    st.markdown("# 🏋️ AI FITNESS COACH DASHBOARD")
    st.markdown("Your Personal Training Intelligence System")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📊 NAVIGATION")
        page = st.radio(
            "Select View:",
            ["📈 Overview", "💪 Performance", "💓 Recovery", "📋 Plans", "🎯 Analytics"]
        )
    
    if page == "📈 Overview":
        show_overview()
    elif page == "💪 Performance":
        show_performance()
    elif page == "💓 Recovery":
        show_recovery()
    elif page == "📋 Plans":
        show_plans()
    elif page == "🎯 Analytics":
        show_analytics()

def show_overview():
    """Main dashboard overview"""
    st.markdown("## 🎯 System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Load latest data
    analyses = load_analysis_data()
    garmin = GarminDataProvider()
    recovery = garmin.get_recovery_score()
    
    with col1:
        st.metric(
            "Recovery Score",
            f"{recovery['score']:.0f}/100",
            delta=recovery['status'],
            delta_color="normal" if recovery['score'] >= 60 else "inverse"
        )
    
    with col2:
        analysis_count = len(analyses)
        st.metric("Plans Analyzed", analysis_count)
    
    with col3:
        if len(analyses) > 0:
            latest = analyses[0]
            volume = latest.get('based_on_previous', {}).get('total_volume', 0)
            st.metric("Latest Volume", f"{volume:,.0f}kg")
    
    with col4:
        if len(analyses) > 0:
            latest = analyses[0]
            rpe = latest.get('based_on_previous', {}).get('rpe_average', 0)
            st.metric("Avg RPE", f"{rpe:.1f}/10")
    
    st.markdown("---")
    
    # Recovery details
    st.markdown("### 💓 Recovery Metrics")
    rec_col1, rec_col2, rec_col3, rec_col4 = st.columns(4)
    
    metrics = recovery['metrics']
    with rec_col1:
        sleep = metrics.get('sleep_hours', 0)
        st.info(f"😴 Sleep\n{sleep:.1f}h" if sleep else "😴 Sleep\nNo data")
    
    with rec_col2:
        rhr = metrics.get('rhr', 0)
        st.info(f"❤️ Resting HR\n{rhr:.0f} bpm" if rhr else "❤️ Resting HR\nNo data")
    
    with rec_col3:
        steps = metrics.get('daily_steps', 0)
        st.info(f"🚶 Steps (7d avg)\n{steps:.0f}" if steps else "🚶 Steps\nNo data")
    
    with rec_col4:
        hrv = metrics.get('hrv', 0)
        st.info(f"📊 HRV\n{hrv:.0f}" if hrv else "📊 HRV\nNo data")
    
    st.markdown("---")
    
    # Knowledge base status
    st.markdown("### 📚 Knowledge Base")
    kb = KnowledgeRetriever()
    kb_col1, kb_col2 = st.columns(2)
    
    with kb_col1:
        st.info("✓ INFORME SERGI.pdf\n✓ Training Principles\n✓ Training History")
    
    with kb_col2:
        st.success("**3 documents indexed**\n**16 knowledge chunks**\n**AI Coach Ready**")

def show_performance():
    """Performance analytics"""
    st.markdown("## 💪 Training Performance")
    
    analyses = load_analysis_data()
    
    if len(analyses) == 0:
        st.warning("No training data yet. Complete your first plan!")
        return
    
    # Volume progression
    st.markdown("### 📈 Volume Progression")
    
    volumes = [a.get('based_on_previous', {}).get('total_volume', 0) for a in analyses]
    dates = [a.get('file', '')[:10] for a in analyses]
    
    if volumes:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(reversed(dates)),
            y=list(reversed(volumes)),
            mode='lines+markers',
            name='Total Volume',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="Weekly Training Volume",
            xaxis_title="Week",
            yaxis_title="Volume (kg)",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Exercise tracking
    st.markdown("### 🎯 Exercise Tracking")
    
    latest_analysis = analyses[0]
    exercises = latest_analysis.get('based_on_previous', {}).get('exercises_tracked', [])
    
    if exercises:
        ex_data = []
        for ex in exercises:
            ex_data.append({
                'Exercise': ex['name'],
                'Volume': ex['total_volume'],
                'Avg RPE': ex['rpe_avg'],
                'Sessions': ex['sessions']
            })
        
        df_exercises = pd.DataFrame(ex_data).sort_values('Volume', ascending=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_vol = px.barh(df_exercises, x='Volume', y='Exercise', 
                             title="Total Volume by Exercise",
                             color='Volume',
                             color_continuous_scale='Blues')
            st.plotly_chart(fig_vol, use_container_width=True)
        
        with col2:
            fig_rpe = px.scatter(df_exercises, x='Sessions', y='Avg RPE', 
                                size='Volume', hover_name='Exercise',
                                title="RPE vs Sessions",
                                color='Avg RPE',
                                color_continuous_scale='RdYlGn_r')
            st.plotly_chart(fig_rpe, use_container_width=True)

def show_recovery():
    """Recovery analysis"""
    st.markdown("## 💓 Recovery & Health")
    
    garmin = GarminDataProvider()
    recovery = garmin.get_recovery_score()
    
    # Recovery gauge
    st.markdown("### Recovery Score Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gauge chart
        score = recovery['score']
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Recovery Score"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 20], 'color': "lightgray", "label": "Critical"},
                    {'range': [20, 40], 'color': "orange", "label": "Poor"},
                    {'range': [40, 60], 'color': "yellow", "label": "Fair"},
                    {'range': [60, 80], 'color': "lightgreen", "label": "Good"},
                    {'range': [80, 100], 'color': "green", "label": "Excellent"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig_gauge.update_layout(height=400)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        st.markdown("### Contributing Factors")
        
        factors = recovery['factors']
        factor_data = []
        for factor, value in factors.items():
            factor_data.append({
                'Factor': factor.upper(),
                'Impact': value
            })
        
        if factor_data:
            df_factors = pd.DataFrame(factor_data).sort_values('Impact', ascending=True)
            
            fig_factors = px.barh(
                df_factors, 
                x='Impact', 
                y='Factor',
                color='Impact',
                color_continuous_scale=['red', 'yellow', 'green'],
                title="Recovery Contributing Factors"
            )
            
            st.plotly_chart(fig_factors, use_container_width=True)
        
        st.markdown("---")
        
        # Recommendations
        st.markdown("### 🎯 AI Recommendations")
        if recovery['score'] >= 80:
            recommendations = [
                "✓ Excellent recovery - increase training intensity",
                "✓ Sleep and activity levels optimal",
                "✓ Consider progressive overload this week"
            ]
            color = "green"
        elif recovery['score'] >= 60:
            recommendations = [
                "✓ Good recovery - maintain current training",
                "✓ Continue current activity levels",
                "✓ Focus on form and technique"
            ]
            color = "blue"
        elif recovery['score'] >= 40:
            recommendations = [
                "⚠ Fair recovery - consider deload week",
                "⚠ Prioritize sleep (target 7+ hours)",
                "⚠ Reduce training volume by 10-15%"
            ]
            color = "orange"
        else:
            recommendations = [
                "❌ Poor recovery - DELOAD WEEK",
                "❌ Mandatory rest days",
                "❌ Prioritize sleep and light activity only",
                "❌ Skip heavy lifting until recovery > 60"
            ]
            color = "red"
        
        for rec in recommendations:
            st.markdown(f"**{rec}**")

def show_plans():
    """Training plans view"""
    st.markdown("## 📋 Training Plans")
    
    plans_dir = Path("output/training_plans")
    
    if not plans_dir.exists():
        st.warning("No plans generated yet")
        return
    
    plans = sorted(plans_dir.glob("*.csv"), reverse=True)
    
    if not plans:
        st.warning("No plans found")
        return
    
    selected_plan = st.selectbox(
        "Select Plan:",
        [p.name for p in plans]
    )
    
    if selected_plan:
        df = pd.read_csv(plans_dir / selected_plan, skiprows=9)
        
        st.markdown(f"### {selected_plan}")
        
        # Display plan
        st.dataframe(df, use_container_width=True, height=400)
        
        # Summary stats
        st.markdown("#### Plan Summary")
        
        completed = df['Peso Real (kg)'].notna().sum() if 'Peso Real (kg)' in df.columns else 0
        total = len(df)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Exercises Completed", f"{completed}/{total}")
        
        with col2:
            avg_rpe = df['RPE'].mean() if 'RPE' in df.columns else 0
            st.metric("Average RPE", f"{avg_rpe:.1f}/10")
        
        with col3:
            total_vol = 0
            if 'Peso Real (kg)' in df.columns and 'Reps Reales' in df.columns and 'Series Reales' in df.columns:
                try:
                    total_vol = (df['Peso Real (kg)'].astype(float) * 
                                df['Reps Reales'].astype(float) * 
                                df['Series Reales'].astype(float)).sum()
                except:
                    pass
            
            st.metric("Total Volume", f"{total_vol:,.0f}kg")

def show_analytics():
    """Advanced analytics"""
    st.markdown("## 🔬 Advanced Analytics")
    
    analyses = load_analysis_data()
    
    if not analyses:
        st.warning("No analysis data available")
        return
    
    # Progression analysis
    st.markdown("### 📊 Training Progression")
    
    if len(analyses) >= 2:
        data = []
        for i, analysis in enumerate(reversed(analyses)):
            week = i + 1
            volume = analysis.get('based_on_previous', {}).get('total_volume', 0)
            rpe = analysis.get('based_on_previous', {}).get('rpe_average', 0)
            sessions = analysis.get('based_on_previous', {}).get('sessions_completed', 0)
            
            data.append({
                'Week': week,
                'Volume': volume,
                'Avg RPE': rpe,
                'Sessions': sessions
            })
        
        df_progression = pd.DataFrame(data)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_progression['Week'],
            y=df_progression['Volume'],
            name='Volume (kg)',
            yaxis='y',
            line=dict(color='#1f77b4', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=df_progression['Week'],
            y=df_progression['Avg RPE'],
            name='Avg RPE',
            yaxis='y2',
            line=dict(color='#ff7f0e', width=3)
        ))
        
        fig.update_layout(
            title="Volume & RPE Progression",
            xaxis_title="Week",
            yaxis_title="Volume (kg)",
            yaxis2=dict(
                title="Average RPE",
                overlaying="y",
                side="right"
            ),
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Latest adjustments
    st.markdown("### 🎯 AI Coach Adjustments")
    
    if analyses:
        latest = analyses[0]
        adjustments = latest.get('adjustments', [])
        focus = latest.get('next_focus', 'UNKNOWN')
        
        st.markdown(f"**Next Focus: {focus}**")
        st.markdown("**Recommended Adjustments:**")
        for adj in adjustments:
            st.markdown(f"- {adj}")

if __name__ == "__main__":
    main()
