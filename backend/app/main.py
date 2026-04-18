from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .routes import export, mcqs, scrape, telegram

settings = get_settings()

app = FastAPI(title="TeleMCQ API", version="1.0.0")

origins = [o.strip() for o in settings.FRONTEND_ORIGIN.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telegram.router)
app.include_router(scrape.router)
app.include_router(mcqs.router)
app.include_router(export.router)


@app.get("/")
def health():
    return {"ok": True, "service": "telemcq"}
