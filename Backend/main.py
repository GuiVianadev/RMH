from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from documents.routes import router as document_router

app = FastAPI(title="RMH Backend API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.include_router(document_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}