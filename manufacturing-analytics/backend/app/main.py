"""
Manufacturing Intelligence & Operations Analytics Platform
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import dashboard, production, machines, quality, maintenance, inventory, orders, alerts

app = FastAPI(
    title="Manufacturing Intelligence & Operations Analytics API",
    description=(
        "REST API for the Manufacturing Intelligence Platform. "
        "Provides KPIs, production analytics, quality metrics, "
        "machine utilization, inventory status, and operational alerts."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(dashboard.router)
app.include_router(production.router)
app.include_router(machines.router)
app.include_router(quality.router)
app.include_router(maintenance.router)
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(alerts.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Manufacturing Analytics API is running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
