"""Dashboard web route."""

import json
from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.calculations import (
    calculate_networth,
    get_networth_history,
    get_allocation_comparison,
    get_income_summary,
    calculate_modified_dietz_return,
    get_daily_performance_series,
)
from app.web.dependencies import templates

router = APIRouter()


def _json_serial(obj):
    """JSON serializer for non-standard types."""
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    """Main dashboard view."""
    networth = calculate_networth(db)
    allocation = get_allocation_comparison(db)
    history = get_networth_history(db, months=12)
    income_summary = get_income_summary(db)
    modified_dietz = calculate_modified_dietz_return(db)
    daily_series = get_daily_performance_series(db)

    chart_data = {
        "history": history,
        "allocation": allocation.get("allocations", []),
        "income": income_summary.get("by_type", {}),
        "daily_series": daily_series.get("series", []),
    }

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "networth": networth,
            "allocation": allocation,
            "income_summary": income_summary,
            "modified_dietz": modified_dietz,
            "chart_data_json": json.dumps(chart_data, default=_json_serial),
        },
    )
