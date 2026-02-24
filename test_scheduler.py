import os
import sys
import time
import logging
from datetime import datetime

# Add the parent directory to the path so we can import modules from it
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('scheduler_test')

# Import FastAPI and our scheduler setup
from fastapi import FastAPI
from scheduler_config import setup_scheduler

# Mock the database connection function
def mock_conectar_db():
    logger.info("Mock database connection called")
    # Return None to simulate connection failure or an object with close method to simulate success
    class MockConnection:
        def is_connected(self):
            return True
        def close(self):
            logger.info("Mock connection closed")
    return MockConnection()

def run_test():
    """Run a test of the scheduler configuration"""
    logger.info("===============================================")
    logger.info("Starting scheduler test at %s", datetime.now())
    logger.info("===============================================")
    
    # Create a FastAPI app
    app = FastAPI()
    
    try:
        # Set up the scheduler
        scheduler = setup_scheduler(app, mock_conectar_db)
          # Log the configured jobs
        logger.info("Configured jobs:")
        for job in scheduler.get_jobs():
            try:
                logger.info(f"  - {job.id}: {job.name}, next run: {job.next_run_time}")
            except AttributeError:
                # Handle case where next_run_time might not be available
                logger.info(f"  - {job.id}: {job.name}, next run: not available")
        
        # Manually trigger the startup event to start the scheduler
        for event_handler in app.router.on_startup:
            try:
                # Some handlers might be async so we need to handle both cases
                import inspect
                if inspect.iscoroutinefunction(event_handler):
                    import asyncio
                    asyncio.run(event_handler())
                else:
                    event_handler()
                logger.info(f"Event handler {event_handler.__name__} executed successfully")
            except Exception as e:
                logger.error(f"Error in event handler {event_handler.__name__}: {e}", exc_info=True)
        
        # Wait for a minute to see if the test job runs
        logger.info("Waiting for 70 seconds to see test job execution...")
        time.sleep(70)
        
        # Shutdown the scheduler
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Scheduler shutdown successful")
        else:
            logger.warning("Scheduler was not running")
            
        logger.info("Test completed successfully")
        
    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
        
    logger.info("===============================================")
    logger.info("Test completed at %s", datetime.now())
    logger.info("===============================================")

if __name__ == "__main__":
    run_test()
