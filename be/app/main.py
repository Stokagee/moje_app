from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import setup_logging
from app.api.endpoints.form_data import router as form_data_router
from app.api.endpoints.couriers import router as couriers_router
from app.api.endpoints.orders import router as orders_router
from app.api.endpoints.dispatch import router as dispatch_router
from app.database import engine, Base
# DŮLEŽITÉ: naimportovat modely před create_all, aby se tabulky vytvořily
from app.models import form_data as _model_form_data  # noqa: F401
from app.models import attachment as _model_attachment  # noqa: F401
from app.models import instruction as _model_instruction  # noqa: F401
from app.models import courier as _model_courier  # noqa: F401
from app.models import order as _model_order  # noqa: F401
from app.models import dispatch_log as _model_dispatch_log  # noqa: F401

# Vytvoření tabulek (pro vývoj, v produkci použít migrace)
Base.metadata.create_all(bind=engine)

# Nastavení logování
setup_logging()

app = FastAPI(
    title="Moje App API",
    version="1.0.0",
    description="API pro formuláře a Food Delivery službu"
)

# CORS - allow requests from mobile apps and development clients
# In production, replace allow_origins with explicit trusted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Přidání routerů
app.include_router(form_data_router, prefix="/api/v1", tags=["form"])
app.include_router(couriers_router, prefix="/api/v1", tags=["couriers"])
app.include_router(orders_router, prefix="/api/v1", tags=["orders"])
app.include_router(dispatch_router, prefix="/api/v1", tags=["dispatch"])

@app.get("/")
def root():
    return {"message": "Moje App API is running!", "docs": "/docs"}