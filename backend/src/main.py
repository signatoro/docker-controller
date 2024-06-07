import logging
import asyncio
import argparse
from logging.handlers import RotatingFileHandler

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from api.routs import router as backend_router
from api.minecraftRoutes import McRoutes
from util.depends import check_periodically
from controller.minecraftControllers import McContainerController

def run_start():
    app = FastAPI()

    # Allow all origins for CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    set_up_logging()

    app.include_router(backend_router)
    
    mc_controller = McContainerController()
    mc_router = McRoutes(mc_controller)

    app.include_router(mc_router.router)

    asyncio.create_task(check_periodically(mc_controller.check_servers, 5))

    return app

def set_up_logging(level_str: str | None = 'INFO', log_file_size: int | None = 1):
    """
    Set up logging configuration.

    Args:
        level_str (str): The logging level as a string. Valid values are
                        'DEBUG', 'CRITICAL', 'ERROR', 'WARNING', and 'INFO'.
        log_file_size (int, optional): The maximum size of the log file in megabytes. Defaults to 1.

    Returns:
        None
    """
    if level_str == 'DEBUG':
        logging_level = logging.DEBUG
    elif level_str == 'CRITICAL':
        logging_level = logging.CRITICAL
    elif level_str == 'ERROR':
        logging_level = logging.ERROR
    elif level_str == 'WARNING':
        logging_level = logging.WARNING
    else:
        logging_level = logging.INFO

    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')

    # Add a rotating file handler to limit the log file size
    file_handler = RotatingFileHandler(
        'server_controller.log',
        maxBytes=1024*1024*log_file_size,
        backupCount=5)
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logging.getLogger().addHandler(file_handler)

    return file_handler


if __name__ == '__main__':
    uvicorn.run("main:run_start", host="0.0.0.0", port=8000, reload="True", factory=True)
