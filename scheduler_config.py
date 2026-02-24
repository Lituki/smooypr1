"""
Módulo de configuración del scheduler para la generación automática de procesos.
Este módulo configura APScheduler y define las funciones que generan procesos diarios,
semanales y mensuales de forma automática.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('scheduler')

def setup_scheduler(app, conectar_db):
    """
    Configures and initializes the scheduler for automatic process generation.
    """
    scheduler = AsyncIOScheduler()
    
    # For testing - add a job that runs every minute to verify scheduler is working
    def test_scheduler_job():
        logger.info("==== TEST JOB RUNNING ==== Scheduler is working correctly!")
    
    # Add a test job that runs every minute to verify the scheduler is working
    scheduler.add_job(
        test_scheduler_job,
        'interval',
        minutes=1,
        id='test_job',
        name='Test Job (Runs every minute)',
        replace_existing=True,
        max_instances=1
    )
    
    # Define synchronous wrapper functions for the scheduler    
    def generar_procesos_diarios_v2():
        """Wrapper for process generation to handle async functions in scheduler"""
        try:
            logger.info("Iniciando generación de procesos diarios...")
            conexion = conectar_db()
            if conexion is None:
                logger.error("Error: No se pudo conectar a la base de datos")
                return
            
            cursor = None
            try:
                cursor = conexion.cursor(dictionary=True)
                
                # Obtener establecimientos activos con su nombre
                cursor.execute("SELECT id, nombre FROM establecimientos WHERE estado = 'activo'")
                establecimientos = cursor.fetchall()
                
                fecha_actual = datetime.now().strftime('%Y-%m-%d')
                
                # Tipos de procesos diarios
                tipos_diarios = ["APERTURA", "CIERRE", "TRASCURSO DE JORNADA"]
                
                # Horarios para cada tipo
                horarios = {
                    "APERTURA": "07:00",
                    "CIERRE": "21:00",
                    "TRASCURSO DE JORNADA": "14:00"
                }
                
                # Contador de procesos creados y existentes
                procesos_creados = 0
                procesos_existentes = 0
                
                # Por cada establecimiento, crear los tres tipos de procesos diarios
                for establecimiento in establecimientos:
                    for tipo in tipos_diarios:
                        # Verificar si ya existe un proceso de este tipo para este establecimiento y fecha
                        cursor.execute("""
                            SELECT id FROM procesos2 
                            WHERE tipo_proceso = %s 
                            AND establecimiento_id = %s 
                            AND fecha_inicio = %s
                        """, (tipo, establecimiento["id"], fecha_actual))
                        
                        proceso_existente = cursor.fetchone()
                        
                        if proceso_existente:
                            # El proceso ya existe, no crear uno nuevo
                            procesos_existentes += 1
                            continue
                        
                        # Datos para el proceso
                        datos_proceso = {
                            "tipo_proceso": tipo,
                            "descripcion": f"Proceso de {tipo}",
                            "frecuencia": "Diaria",
                            "horario": horarios[tipo],
                            "fecha_inicio": fecha_actual,
                            "fecha_fin": fecha_actual,
                            "estado": "Verificación pendiente",
                            "ubicacion": establecimiento["nombre"],
                            "establecimiento_id": establecimiento["id"],
                            "usuario_id": None  # Sistema automático
                        }
                        
                        # Insertar el proceso en la tabla procesos2
                        cursor.execute("""
                            INSERT INTO procesos2 (tipo_proceso, descripcion, frecuencia, horario, 
                            fecha_inicio, fecha_fin, estado, ubicacion, establecimiento_id, usuario_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            datos_proceso["tipo_proceso"],
                            datos_proceso["descripcion"],
                            datos_proceso["frecuencia"],
                            datos_proceso["horario"],
                            datos_proceso["fecha_inicio"],
                            datos_proceso["fecha_fin"],
                            datos_proceso["estado"],
                            datos_proceso["ubicacion"],
                            datos_proceso["establecimiento_id"],
                            datos_proceso["usuario_id"]
                        ))
                        procesos_creados += 1
                
                conexion.commit()
                logger.info(f"Procesos diarios: {procesos_creados} creados")
            except Exception as e:
                logger.error(f"Error al generar procesos diarios: {str(e)}")
            finally:
                if cursor:
                    cursor.close()
                if conexion and conexion.is_connected():
                    conexion.close()
        except Exception as e:
            logger.error(f"Error general en generación de procesos diarios: {str(e)}")    
    def generar_procesos_semanales_v2():
        """Wrapper for weekly process generation to handle async functions in scheduler"""
        try:
            logger.info("Iniciando generación de procesos semanales...")
            conexion = conectar_db()
            if conexion is None:
                logger.error("Error: No se pudo conectar a la base de datos")
                return
            
            cursor = None
            try:
                cursor = conexion.cursor(dictionary=True)
                
                # Obtener establecimientos activos con su nombre
                cursor.execute("SELECT id, nombre FROM establecimientos WHERE estado = 'activo'")
                establecimientos = cursor.fetchall()
                
                fecha_actual = datetime.now().strftime('%Y-%m-%d')
                hora_actual = "07:00"  # Hora fija para procesos semanales
                
                # Calcular la fecha de fin (una semana después)
                fecha_fin = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                
                # Contador de procesos creados y existentes
                procesos_creados = 0
                procesos_existentes = 0
                
                # Por cada establecimiento, crear proceso semanal
                for establecimiento in establecimientos:
                    # Verificar si ya existe un proceso semanal para este establecimiento y fecha
                    cursor.execute("""
                        SELECT id FROM procesos2 
                        WHERE tipo_proceso = 'PROCESO SEMANAL' 
                        AND establecimiento_id = %s 
                        AND fecha_inicio = %s
                    """, (establecimiento["id"], fecha_actual))
                    
                    proceso_existente = cursor.fetchone()
                    
                    if proceso_existente:
                        # El proceso ya existe, no crear uno nuevo
                        procesos_existentes += 1
                        continue
                    
                    # Datos para el proceso semanal
                    datos_proceso = {
                        "tipo_proceso": "PROCESO SEMANAL",
                        "descripcion": f"Proceso de SEMANAL",
                        "frecuencia": "Semanal",
                        "horario": hora_actual,
                        "fecha_inicio": fecha_actual,
                        "fecha_fin": fecha_fin,
                        "estado": "Verificación pendiente",
                        "ubicacion": establecimiento["nombre"],
                        "establecimiento_id": establecimiento["id"],
                        "usuario_id": None
                    }
                    
                    # Insertar el proceso en la tabla procesos2
                    cursor.execute("""
                        INSERT INTO procesos2 (tipo_proceso, descripcion, frecuencia, horario, 
                        fecha_inicio, fecha_fin, estado, ubicacion, establecimiento_id, usuario_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        datos_proceso["tipo_proceso"],
                        datos_proceso["descripcion"],
                        datos_proceso["frecuencia"],
                        datos_proceso["horario"],
                        datos_proceso["fecha_inicio"],
                        datos_proceso["fecha_fin"],
                        datos_proceso["estado"],
                        datos_proceso["ubicacion"],
                        datos_proceso["establecimiento_id"],
                        datos_proceso["usuario_id"]
                    ))
                    procesos_creados += 1
                
                conexion.commit()
                logger.info(f"Procesos semanales: {procesos_creados} creados")
            except Exception as e:
                logger.error(f"Error al generar procesos semanales: {str(e)}")
            finally:
                if cursor:
                    cursor.close()
                if conexion and conexion.is_connected():
                    conexion.close()
        except Exception as e:
            logger.error(f"Error general en generación de procesos semanales: {str(e)}")    
            
    def generar_procesos_mensuales_v2():
        """Wrapper for monthly process generation to handle async functions in scheduler"""
        try:
            logger.info("Iniciando generación de procesos mensuales...")
            conexion = conectar_db()
            if conexion is None:
                logger.error("Error: No se pudo conectar a la base de datos")
                return
            
            cursor = None
            try:
                cursor = conexion.cursor(dictionary=True)
                
                # Obtener establecimientos activos con su nombre
                cursor.execute("SELECT id, nombre FROM establecimientos WHERE estado = 'activo'")
                establecimientos = cursor.fetchall()
                
                fecha_actual = datetime.now().strftime('%Y-%m-%d')
                hora_actual = "07:00"  # Hora fija para procesos mensuales
                
                # Calcular la fecha de fin (un mes después aproximadamente)
                fecha_fin = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                
                # Contador de procesos creados y existentes
                procesos_creados = 0
                procesos_existentes = 0
                
                # Por cada establecimiento, crear proceso mensual
                for establecimiento in establecimientos:
                    # Verificar si ya existe un proceso mensual para este establecimiento y fecha
                    cursor.execute("""
                        SELECT id FROM procesos2 
                        WHERE tipo_proceso = 'PROCESO MENSUAL' 
                        AND establecimiento_id = %s 
                        AND fecha_inicio = %s
                    """, (establecimiento["id"], fecha_actual))
                    
                    proceso_existente = cursor.fetchone()
                    
                    if proceso_existente:
                        # El proceso ya existe, no crear uno nuevo
                        procesos_existentes += 1
                        continue
                    
                    # Datos para el proceso mensual
                    datos_proceso = {
                        "tipo_proceso": "PROCESO MENSUAL",
                        "descripcion": f"Proceso de MENSUAL",
                        "frecuencia": "Mensual",
                        "horario": hora_actual,
                        "fecha_inicio": fecha_actual,
                        "fecha_fin": fecha_fin,
                        "estado": "Verificación pendiente",
                        "ubicacion": establecimiento["nombre"],
                        "establecimiento_id": establecimiento["id"],
                        "usuario_id": None
                    }
                    
                    # Insertar el proceso en la tabla procesos2
                    cursor.execute("""
                        INSERT INTO procesos2 (tipo_proceso, descripcion, frecuencia, horario, 
                        fecha_inicio, fecha_fin, estado, ubicacion, establecimiento_id, usuario_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        datos_proceso["tipo_proceso"],
                        datos_proceso["descripcion"],
                        datos_proceso["frecuencia"],
                        datos_proceso["horario"],
                        datos_proceso["fecha_inicio"],
                        datos_proceso["fecha_fin"],
                        datos_proceso["estado"],
                        datos_proceso["ubicacion"],
                        datos_proceso["establecimiento_id"],
                        datos_proceso["usuario_id"]
                    ))
                    procesos_creados += 1
                
                conexion.commit()
                logger.info(f"Procesos mensuales: {procesos_creados} creados")
            except Exception as e:
                logger.error(f"Error al generar procesos mensuales: {str(e)}")
            finally:
                if cursor:
                    cursor.close()
                if conexion and conexion.is_connected():
                    conexion.close()
        except Exception as e:
            logger.error(f"Error general en generación de procesos mensuales: {str(e)}")

    # Configure scheduled jobs with proper IDs and error handling
    scheduler.add_job(
        generar_procesos_diarios_v2, 
        'cron', 
        hour=13, 
        minute=12,
        id='procesos_diarios',
        name='Generación de procesos diarios',
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=3600,  # Allow the job to run even if it's up to 1 hour late
        coalesce=True  # Only run once if multiple executions are missed
    )
    
    scheduler.add_job(
        generar_procesos_semanales_v2, 
        'cron', 
        day_of_week='mon', 
        hour=7, 
        minute=0,
        id='procesos_semanales',
        name='Generación de procesos semanales',
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=3600,
        coalesce=True
    )
    
    scheduler.add_job(
        generar_procesos_mensuales_v2, 
        'cron', 
        day=1, 
        hour=7, 
        minute=0,
        id='procesos_mensuales',
        name='Generación de procesos mensuales',
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=3600,
        coalesce=True
    )
      # Add startup event handler for the application
    @app.on_event("startup")
    async def startup_event():
        try:
            logger.info("Iniciando scheduler para generación automática de procesos...")
            
            # Test if the database connection works before starting the scheduler
            test_conn = conectar_db()
            if test_conn is None:
                logger.error("No se puede conectar a la base de datos. El scheduler podría no funcionar correctamente.")
            else:
                logger.info("Conexión a la base de datos verificada correctamente.")
                if hasattr(test_conn, 'close') and callable(getattr(test_conn, 'close')):
                    test_conn.close()
            
            # Start the scheduler
            if not scheduler.running:
                scheduler.start()
                logger.info("Scheduler iniciado correctamente. Próximas ejecuciones:")
                  # Display scheduled executions for diagnostics
                for job in scheduler.get_jobs():
                    try:
                        logger.info(f"- {job.name}: próxima ejecución {job.next_run_time}")
                    except AttributeError:
                        logger.info(f"- {job.name}: próxima ejecución no disponible")
            else:
                logger.warning("El scheduler ya estaba en ejecución.")
                
        except Exception as e:
            logger.error(f"Error al iniciar el scheduler: {str(e)}", exc_info=True)
            # Try to restart the scheduler
            try:
                if scheduler.running:
                    scheduler.shutdown()
                scheduler.start()
                logger.info("Scheduler reiniciado después de error")
                  # Display scheduled executions again after restart
                for job in scheduler.get_jobs():
                    try:
                        logger.info(f"- {job.name}: próxima ejecución {job.next_run_time}")
                    except AttributeError:
                        logger.info(f"- {job.name}: próxima ejecución no disponible")
            except Exception as e2:
                logger.error(f"No se pudo reiniciar el scheduler: {str(e2)}", exc_info=True)
    
    @app.on_event("shutdown")
    async def shutdown_event():
        try:
            logger.info("Cerrando el scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler cerrado correctamente")
        except Exception as e:
            logger.error(f"Error al cerrar el scheduler: {str(e)}")
    
    return scheduler
