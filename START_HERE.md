# 🚀 COMPLETE AI FITNESS COACH SETUP

## ✅ Sistema Implementado

Tu proyecto está 100% funcional con:

- **✓ AI Coach Local** - Genera planes en CSV
- **✓ Garmin Integration** - Lee recuperación en tiempo real
- **✓ Dashboard Local** - Visualiza todo el progreso
- **✓ PR Predictor** - Predice RMs futuros
- **✓ Knowledge Base** - Con INFORME SERGI + Principios

---

## 🎮 COMANDOS RÁPIDOS

### 1️⃣ Generar Plan Nueva Semana
```bash
python ai_coach_local.py generate
```
Crea: `output/training_plans/plan_YYYYMMDD.csv`

### 2️⃣ Completa los Entrenamientos
Abre el CSV en Excel/Sheets y completa después de entrenar:
- `Series Reales`, `Reps Reales`, `Peso Real`, `RPE`, `Notas`

### 3️⃣ Analizar & Generar Siguiente Plan
```bash
python ai_coach_local.py analyze output/training_plans/plan_20260307.csv
```

Automáticamente: 
- Analiza desempeño real
- Lee Garmin (recuperación, sueño, pasos)
- Consulta Knowledge Base
- Genera siguiente plan con adjustments

### 4️⃣ Ver Dashboard En Vivo
```bash
streamlit run dashboard.py
```
Abre: **http://localhost:8501**

### 5️⃣ Ver Predicciones de RMs (PR Predictor)
```bash
python pr_predictor.py
```
Requisito: Mínimo 2 planes completados

---

## 📊 DASHBOARD - Vistas Disponibles

El dashboard está accesible en **http://localhost:8501** con 5 vistas:

### 📈 Overview
- Recovery Score (0-100)
- Plans analyzed
- Training volume
- Average RPE
- Garmin metrics (sueño, HR, pasos)

### 💪 Performance
- Volume progression (gráficas)
- Exercise tracking por ejercicio
- RPE vs sessions analysis

### 💓 Recovery
- Recovery score gauge
- Contributing factors
- AI recommendations según estado

### 📋 Plans
- Lista todos los planes generados
- Preview del plan actual
- Resumen: ejercicios completados, volumen, RPE

### 🔬 Analytics
- Progression analysis (4+ semanas)
- AI Coach adjustments
- Tendencias largo plazo

---

## 🎯 CICLO COMPLETO (Método Recomendado)

### Semana 1
```
Lunes:   python ai_coach_local.py generate          → Plan creado
Tue-Fri: Completa entrenamientos en el CSV
Domingo: python ai_coach_local.py analyze <plan>   → Analiza + genera siguiente
```

### Semana 2+
```
Repite el ciclo...
Dashboard irá acumulando:
  - Progresión de volumen
  - RPE trends
  - Ejercicios con mejor/peor desempeño
  - Predicciones de RMs
```

---

## 🧠 INTELIGENCIA DEL COACH

### ¿Cómo genera planes?
```
Paso 1: Lee INFORME SERGI.pdf          → Tu perfil personal
Paso 2: Lee Training Principles         → Ciencia del entrenamiento
Paso 3: Analiza plan anterior          → Tu desempeño real
Paso 4: Lee Garmin                     → Recuperación actual
Paso 5: Aplica adjustments inteligentes → Siguiente plan

Ejemplo:
- Bench 50kg con RPE 7 → "Listo para 55kg"
- Triceps RPE 8 → "Reducir volumen"
- Calves RPE 5 → "Aumentar peso"
- Sleep 6.5h + Steps 17k → "Mantener intensidad"
```

### Ajustes Importantes

**Recuperación (Garmin)**
```
EXCELLENT  Sleep≥7h + Steps≥15000  → ⬆️  AUMENTAR
GOOD       Sleep≥6h + Steps≥10000  → ➡️  MANTENER
FAIR       Sleep≥5h + Steps≥8000   → ➡️  MANTENER con form focus
POOR       Datos mínimos           → ⬇️  DELOAD
```

**Performance (RPE)**
```
RPE 5-6    → "Fácil" → Aumentar peso
RPE 6-7    → "Óptimo" → Mantener
RPE 8-9    → "Duro" → Mantener volumen
RPE 10     → "Máximo" → Reducir
```

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
AI_Fitness/
├── ai_coach_local.py          ← AI Coach local (no APIs externas)
├── garmin_integration.py       ← Lee Garmin CSV
├── pr_predictor.py             ← Predice RMs futuros
├── dashboard.py                ← Dashboard Streamlit
├── knowledge_retriever.py      ← Busca en Knowledge Base
│
├── output/
│   ├── training_plans/
│   │   ├── plan_20260307.csv          (plan actual)
│   │   └── plan_YYYYMMDD.csv          (planes anteriores)
│   ├── garmin_recovery_report.json    (análisis Garmin)
│   └── pr_predictions.json            (predicciones RMs)
│
├── data/
│   ├── garmin_stats.csv               (Garmin watch data)
│   ├── hevy_stats.csv                 (historial entrenamientos)
│   ├── knowledge_base/
│   │   ├── knowledge.db               (SQLite KB)
│   │   └── raw_pdfs/
│   │       ├── INFORME SERGI.pdf      ← Tu perfil
│   │       ├── Training_Principles.txt
│   │       └── training_history_report.txt
│   └── workout_history/
│       └── analysis_YYYYMMDD_HHMMSS.json (análisis plan)
│
└── COACH_LOCAL_README.md       (documentación detallada)
```

---

## 🔧 REQUISITOS INSTALADOS

```bash
✓ Python 3.12
✓ pandas 2.3.3
✓ numpy 1.26.4
✓ streamlit (para dashboard)
✓ plotly (para gráficas)
✓ pdfplumber (para PDFs)
✓ PyPDF2 (PDFs backup)
```

Si falta algo:
```bash
pip install -r requirements.txt
```

---

## 🎓 EJEMPLOS DE USO

### Ejemplo 1: Primera Semana

**Paso 1: Generar Plan**
```bash
python ai_coach_local.py generate
# Output: plan_20260307.csv creado
```

**Paso 2: Completar After Training**
Abre `plan_20260307.csv`:
```
Lunes       Bench Press   5 AMRAP 50  →  5  8  50  7  "Buena forma"
Lunes       Rows          4  6     -  →  4  6  70  6  "Fuerte"
Martes      Leg Press     4  8    100 →  4  8 100  6  "Profundidad"
...
```

**Paso 3: Analizar & Generar Siguiente**
```bash
python ai_coach_local.py analyze plan_20260307.csv
```

Coach analiza:
```
✓ 5 sesiones completadas
✓ 34,800kg volumen total
✓ RPE 5.8 promedio (óptimo)
✓ Garmin: Recuperación EXCELLENT
  - Sleep 6.5h
  - Pasos 17,000
  - HR reposo 48
  - HRV: Bueno

Adjustments para siguiente:
✓ Bench: 50kg x 8 reps → AUMENTAR A 55kg
✓ Triceps: RPE 8 → Reducir volumen
✓ Recuperación excelente → Mantener intensidad
```

Genera: `plan_20260314.csv` con adjustments

### Ejemplo 2: Monitorear en Dashboard

```bash
streamlit run dashboard.py
# Abre http://localhost:8501
```

**Vista: 💪 Performance**
- Gráfica de volumen por semana
- Cada ejercicio: volumen total, RPE promedio
- Detecta tendencias (↑ progresión, ↓ plateau)

**Vista: 💓 Recovery**
- Recovery Score gauge (0-100)
- Factores contributing (sleep, HR, activity)
- Recomendaciones AI

**Vista: 🔬 Analytics**
- Predicción de RMs 4 semanas adelante
- Ejercicios necesitando atención
- Top growth opportunities

### Ejemplo 3: Predicciones (después 2+ ciclos)

```bash
python pr_predictor.py

Resultado:
================================================================================
🎯 PR PREDICTION ENGINE
================================================================================

📊 Analyzing 15 exercises...

Bench Press
  Current Volume:    2,000 kg
  Predicted (4w):    2,400 kg
  Projected Gain:      400 kg
  Confidence:         65%
  Status:    STRONG_PROGRESSION
  Action:    ✓ Strong progression - maintain current strategy

... [más ejercicios] ...

💪 TOP GROWTH OPPORTUNITIES
1. Bench Press
   Potential Gain: 100kg/week
   Confidence: 65%
================================================================================
```

---

## 📞 TROUBLESHOOTING

### Dashboard no abre
```bash
# Kill streamlit y reinicia
taskkill /F /IM streamlit.exe
streamlit run dashboard.py
```

### Garmin data "Not found"
- Asegúrate que `data/garmin_stats.csv` existe
- Si está corrupto: descarga nuevo de Garmin Connect

### PR Predictor "Insufficient data"
- Necesitas mínimo 2 planes completados
- Sigue la rutina 2 semanas primero

### CSV no se analiza
- Verifica que `Peso Real (kg)` esté completado
- Format: use numbers sin unidades

---

## 🚀 ROADMAP FUTURO

**Phase 2 (Ya implementado):**
- ✅ Garmin integration con recovery score
- ✅ Dashboard local con visualización
- ✅ PR prediction engine

**Phase 3 (Próximo):**
- 🔄 Ejercicio recommendations por weak points
- 🔄 Macros calculator basado en Garmin
- 🔄 Export a PDF monthly reports
- 🔄 Mobile app integration

---

## ✅ SISTEMA COMPLETAMENTE OPERACIONAL

Tu coach está listo. Emppieza con:

```bash
python ai_coach_local.py generate
```

Luego:
1. Entrena la semana
2. Completa el CSV
3. Ejecuta: `python ai_coach_local.py analyze <plan>.csv`
4. Repite

**Dashboard en vivo: `python streamlit run dashboard.py`**

¡Tu sistema de entrenamiento personalizado está listo!
