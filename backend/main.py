
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routs import router as backend_router
from src.depends import check_container, check_periodically


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

    app.include_router(backend_router)

    asyncio.create_task(check_periodically(check_container, 5))

    return app


if __name__ == '__main__':
    uvicorn.run("main:run_start", host="0.0.0.0", port=8000, reload="True", factory=True)
