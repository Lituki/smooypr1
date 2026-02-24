"""
Utility script to manually trigger scheduler jobs
"""
import sys
import logging
import argparse
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("manual_processes.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('manual_processes')

# Import the necessary modules
from main import conectar_db

def run_manual_job(job_type):
    """Run a specific job manually"""
    logger.info(f"====== Starting manual generation of {job_type} processes ======")
    
    try:
        if job_type == "daily":
            from scheduler_config import generar_procesos_diarios_v2
            generar_procesos_diarios_v2()
            logger.info("Daily processes have been generated successfully")
            
        elif job_type == "weekly":
            from scheduler_config import generar_procesos_semanales_v2
            generar_procesos_semanales_v2()
            logger.info("Weekly processes have been generated successfully")
            
        elif job_type == "monthly":
            from scheduler_config import generar_procesos_mensuales_v2
            generar_procesos_mensuales_v2()
            logger.info("Monthly processes have been generated successfully")
            
        elif job_type == "all":
            from scheduler_config import generar_procesos_diarios_v2, generar_procesos_semanales_v2, generar_procesos_mensuales_v2
            
            logger.info("Generating daily processes...")
            generar_procesos_diarios_v2()
            
            logger.info("Generating weekly processes...")
            generar_procesos_semanales_v2()
            
            logger.info("Generating monthly processes...")
            generar_procesos_mensuales_v2()
            
            logger.info("All processes have been generated successfully")
            
        else:
            logger.error(f"Unknown job type: {job_type}")
            print(f"Error: Unknown job type '{job_type}'. Valid options are: daily, weekly, monthly, all")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error running {job_type} job: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manual process generation tool")
    parser.add_argument(
        "job_type",
        choices=["daily", "weekly", "monthly", "all"],
        help="Type of processes to generate"
    )
    
    args = parser.parse_args()
    success = run_manual_job(args.job_type)
    
    if success:
        print(f"Successfully generated {args.job_type} processes. See manual_processes.log for details.")
    else:
        print(f"Failed to generate {args.job_type} processes. See manual_processes.log for details.")
        sys.exit(1)
