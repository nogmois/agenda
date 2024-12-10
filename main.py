from fastapi import FastAPI
from app.routes.event_routes import router as event_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(event_router)

@app.get("/")
async def root():
    return {"message": "API is running"}
