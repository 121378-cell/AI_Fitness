# Roadmap de Mejoras — AI Fitness (Garmin-only)

## Orden de ejecución

1. **Fase 0 — Alineación de configuración/documentación** (completada)
2. **Fase 1 — Versionado de esquema SQLite + migraciones incrementales**
3. **Fase 2 — Testing de integración y cobertura**
4. **Fase 3 — Observabilidad y runbooks operativos**
5. **Fase 4 — Refactor progresivo del dashboard**
6. **Fase 5 — Endurecimiento CI/CD**
7. **Fase 6 — Cutover final y estabilización**

## Estado actual

- [x] Eliminadas integraciones externas fuera de alcance del proyecto.
- [x] Proyecto y docs alineados al alcance Garmin-only.
- [x] Validación del sistema en verde (`make ci-check`).
- [~] Fase 1 iniciada: versionado de esquema SQLite (`PRAGMA user_version`) y migración incremental v1 implementados.
- [ ] Siguiente paso: completar validaciones de esquema pre-upsert (Fase 1).

## Criterio de calidad por fase

No se marca una fase como terminada hasta tener:
1. tests en verde,
2. compile checks en verde,
3. pipeline de migración/calidad en verde,
4. documentación actualizada.
