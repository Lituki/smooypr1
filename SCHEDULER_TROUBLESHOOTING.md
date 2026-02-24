# Guía de solución de problemas - Scheduler FastAPI

## Objetivo
Esta guía proporciona pasos para diagnosticar y resolver problemas con el scheduler en la aplicación FastAPI de SMOOY.

## Problema
El scheduler está configurado pero los procesos no se generan automáticamente en los horarios programados:
- Procesos diarios: 7:00 AM todos los días
- Procesos semanales: Lunes a las 7:00 AM
- Procesos mensuales: Día 1 de cada mes a las 7:00 AM

## Verificaciones de diagnóstico

### 1. Verificar logs del scheduler
Revisar el archivo `scheduler.log` en el directorio principal para ver si hay errores o mensajes importantes.

### 2. Verificar si el scheduler se inicia correctamente
```powershell
# Ejecutar el test del scheduler
cd "C:\Users\Asia_Coordinator\Desktop\FastAPI"
python test_scheduler.py
```

### 3. Comprobar conectividad con la base de datos
Verificar que la función `conectar_db()` funciona correctamente y devuelve una conexión válida.

### 4. Comprobar que los trabajos están programados
```powershell
# Iniciar la aplicación y verificar en los logs iniciales
cd "C:\Users\Asia_Coordinator\Desktop\FastAPI"
python -m uvicorn main:app --reload
```

Buscar en los logs mensajes como: `Scheduler iniciado correctamente. Próximas ejecuciones:`

### 5. Ejecutar manualmente los procesos para probar
Abrir el intérprete de Python y ejecutar:
```python
from main import conectar_db
import scheduler_config
from fastapi import FastAPI
app = FastAPI()
scheduler = scheduler_config.setup_scheduler(app, conectar_db)

# Ejecutar directamente las funciones de generación de procesos
from scheduler_config import generar_procesos_diarios_v2
generar_procesos_diarios_v2()
```

## Soluciones para problemas comunes

### El scheduler no se inicia
1. Verificar errores en `scheduler.log`
2. Asegurarse de que no haya errores de sintaxis en `scheduler_config.py`
3. Verificar que las dependencias necesarias están instaladas:
   ```powershell
   pip install apscheduler
   ```

### El scheduler se inicia pero los trabajos no se ejecutan
1. Verificar que los trigger cron están configurados correctamente
2. Asegurarse de que el reloj del sistema esté configurado correctamente
3. Verificar que las funciones generadoras de procesos no tengan errores
4. Asegurarse de que la base de datos está accesible cuando se ejecutan los trabajos

### Errores en la generación de procesos
1. Verificar que las tablas necesarias existen en la base de datos
2. Comprobar que los procesos no se estén duplicando
3. Verificar que la conexión a la base de datos funciona correctamente

## Reinicios manuales
Si el scheduler no está funcionando, puedes reiniciarlo manualmente:

```python
from main import scheduler
scheduler.shutdown(wait=False)
scheduler.start()
```

## Notas importantes
- APScheduler funciona mejor con funciones sincrónicas. Las funciones asíncronas deben ser adaptadas.
- El scheduler puede detenerse si la aplicación principal se cierra.
- El servidor debe mantenerse en ejecución para que el scheduler funcione.
- El reloj del sistema debe estar sincronizado para que los trabajos se ejecuten a la hora correcta.

## Contacto
Si los problemas persisten, contactar al equipo de soporte técnico.
