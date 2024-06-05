
import asyncio
import uvicorn
import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



from api.routs import router as backend_router
from api.minecraftRoutes import McRoutes
from util.depends import check_periodically
from controller.minecraftControllers import McContainerController

def run_start():
    app = FastAPI()

    parser = argparse.ArgumentParser(description='Start Minecraft server with Docker')
    parser.add_argument('--volumes', '-v', type=str, help='List of volumes to mount to the server')


    print(f'{parser.parse_args().volumes}')
    # Allow all origins for CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.include_router(backend_router)
    
    mc_controller = McContainerController()
    mc_router = McRoutes(mc_controller)

    app.include_router(mc_router.router)

    asyncio.create_task(check_periodically(mc_controller.check_servers, 5))

    return app


if __name__ == '__main__':
    uvicorn.run("main:run_start", host="0.0.0.0", port=8000, reload="True", factory=True)
