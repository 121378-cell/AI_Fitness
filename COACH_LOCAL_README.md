# 🏋️ LOCAL AI FITNESS COACH

Sistema completamente local para planificación de entrenamientos. Sin integraciones externas.

## ¿Cómo Funciona?

```
1. COACH GENERA PLAN (CSV)
   ↓
2. TÚ COMPLETAS LOS ENTRENAMIENTOS (Pesos, Reps, RPE)
   ↓
3. DEVUELVES EL CSV AL COACH
   ↓
4. COACH ANALIZA:
   - Tu desempeño real vs planificado
   - Datos de Garmin (Recuperación, NEAT, HR)
   - Conocimiento acumulado
   ↓
5. COACH GENERA SIGUIENTE PLAN (Ajustado)
   ↓
6. CICLO CONTINUO...
```

## Comandos

### Generar Plan Inicial
```bash
python ai_coach_local.py generate
```
Crea: `output/training_plans/plan_YYYYMMDD.csv`

### Analizar & Generar Siguiente
```bash
python ai_coach_local.py analyze output/training_plans/plan_20260307.csv
```

Hace:
1. Analiza tu desempeño en el plan completado
2. Lee datos de Garmin (recuperación, pasos, sueño)
3. Consulta knowledge base (principios, historial)
4. Genera siguiente plan con adjustments inteligentes

### Ver Estado del Sistema
```bash
python ai_coach_local.py status
```

## CSV Format (Plan)

Estructura del archivo generado:

```
PLAN DE ENTRENAMIENTO - AI COACH
Fecha Inicio: 2026-03-07
Estado: INCOMPLETO - Completar después de entrenar

INSTRUCCIONES:
1. Completa cada sesión con tus pesos y repeticiones REALES
2. Marca el RPE (Rate of Perceived Exertion) 1-10
3. Marca notas de cómo te sentiste
4. Devuelve el archivo completado al coach para análisis

Día | Ejercicio | Series Planificadas | ... | Series Reales | Peso Real | RPE | Notas
Lunes | Bench Press | 5 | AMRAP | 50 | 5 | 50 | 7 | Buena forma
...
```

**Campos para completar:**
- `Series Reales` - Cuántas series completaste
- `Reps Reales` - Cuántas reps en cada serie (promedio si varían)
- `Peso Real (kg)` - Peso que usaste
- `RPE` - Rate of Perceived Exertion (1-10)
- `Notas` - Cómo te sentiste, problemas, etc.

## Ciclo Completo

### 1. Día 1 - Generates Plan
```bash
python ai_coach_local.py generate
```
Output: `plan_20260307.csv`

### 2. Days 2-6 - Completa los entrenamientos
Abre `plan_20260307.csv` en Excel/Sheets/LibreOffice
Completa cada fila después de entrenar

### 3. Día 7 - Análisis & Siguiente Plan
```bash
python ai_coach_local.py analyze plan_20260307.csv
```

El coach:
- Analiza desempeño (volumen, RPE, ejercicios)
- Lee Garmin (sueño, pasos, HR)
- Consulta INFORME SERGI + Training Principles
- Genera `plan_20260314.csv` con adjustments

### 4. Semana 2 - Completa nuevo plan
Repite el ciclo...

## Lógica de Adjustments

El coach ajusta el siguiente plan basado en:

### Recuperación (Garmin)
```
EXCELLENT Sleep≥7h + Steps≥15000  → AUMENTAR volumen/intensidad
GOOD      Sleep≥6h + Steps≥10000  → MANTENER intensidad
FAIR      Sleep≥5h                → MANTENER, Enfoque en forma
POOR      Sleep<5h                → REDUCIR volumen (DELOAD)
```

### RPE Analysis
```
RPE < 5   → Aumentar peso (ejercicio fácil)
RPE 6-7   → Óptimo (mantener)
RPE 8-9   → Mantener intensidad
RPE ≥ 10  → Reducir volumen o peso (demasiado duro)
```

### Progresión
Cada semana el coach revisa:
1. ¿Completaste todo? → Aumentar
2. ¿Te sentiste cómodo? (RPE 6-7) → Aumentar
3. ¿Tenías energía? (Garmin recovery GOOD+) → Aumentar
4. Sino → Mantener o reducir

## Conocimiento Utilizado

El coach consulta automáticamente:
- 📄 **INFORME SERGI.pdf** - Tu perfil personal, baselines
- 📚 **Training_Principles.txt** - Principios científicos
- 📊 **Training_History** - Historial de 17+ sesiones previas
- 💓 **Garmin Data** - Datos de recuperación en tiempo real

## Archivos Generados

```
output/training_plans/
├── plan_20260307.csv    (Plan 1)
├── plan_20260314.csv    (Plan 2)
└── plan_20260321.csv    (Plan 3)

data/workout_history/
├── analysis_20260307_142030.json  (Análisis Plan 1)
├── analysis_20260314_142030.json  (Análisis Plan 2)
└── ...
```

## Ejemplo de Flujo

**Semana 1: Generación**
```
Coach: "Basándome en tu INFORME (47 años, Bench 50kg, Prensa 100kg)
         y tu historial (17 sesiones previas), he creado tu plan.
         Tu recuperación según Garmin es EXCELENTE (8h sueño, 22k pasos).
         Plan orientado a PROGRESIÓN."
         
Plan: Bench 50kg 5xAMRAP, Prensa 100kg 4x8, etc.
```

**Semana 2: Análisis → Siguiente**
```
Tu desempeño:
- Bench: 50kg x 8 reps ✓ (RPE 7)
- Prensa: 100kg x 8 reps ✓ (RPE 6)
- Vol total: 41,000kg

Garmin últimos 7 días:
- Sueño: 7.2h promedio ✓
- Pasos: 21,000 promedio ✓
- HR reposo: 48 bpm ✓

Coach: "Recuperación EXCELENTE. Desempeño sólido.
         Siguiente plan: Aumentar Bench a 55kg (nuevo RM).
         Mantener Prensa. Agregar volumen accesorio."
         
Plan: Bench 55kg x 3-5 reps, Prensa 100kg x 4x8 con mayor profundidad, etc.
```

## Sin Dependencias Externas

- ❌ No requiere API de Hevy
- ❌ No requiere conexión a Gemini
- ❌ No requiere Ollama ejecutándose
- ✅ Todo funciona localmente
- ✅ Solo necesita Garmin CSV en `data/garmin_stats.csv`

## Roadmap

1. ✅ Generar planes en CSV
2. ✅ Analizar desempeño completado
3. ✅ Integrar datos Garmin
4. ✅ Ajustes inteligentes por recuperación
5. 🔄 Dashboard local para visualizar progreso
6. 🔄 Predicción de próximas PRs
7. 🔄 Análisis de patrones débiles

---

**Comando rápido para empezar:**
```bash
python ai_coach_local.py generate
```

Completa los entrenamientos en el CSV y vuelve a ejecutar:
```bash
python ai_coach_local.py analyze plan_YYYYMMDD.csv
```
