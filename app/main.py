"""

Voy a levantar un FastAPI porque no se me ocurre otra forma de hacer apps con interacciones web
el esp32 tambien tiene un webserver asi que podría ser buena forma para comunicar ambos lados.
ademas FastAPI tiene soporte nativo para Websockets lo cual es ideal para este tipo de aplicaciones en tiempo real.

"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import usb_router, ai_router
import uvicorn
import os
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(usb_router.router, prefix="/usb", tags=["USB Client"])
app.include_router(ai_router.router, prefix="/ai", tags=["AI Client"])
if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000)))

