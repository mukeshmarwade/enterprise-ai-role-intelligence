from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Role
from backend.schemas import ComparisonResponse
from backend.llm import generate_narrative

router = APIRouter(prefix="/api/compare", tags=["compare"])


@router.get("", response_model=ComparisonResponse)
def compare_roles(
    role_a: str = Query(..., description="Title of first role"),
    role_b: str = Query(..., description="Title of second role"),
    db: Session = Depends(get_db),
):
    a = db.query(Role).filter(Role.title.ilike(role_a)).first()
    b = db.query(Role).filter(Role.title.ilike(role_b)).first()
    if not a or not b:
        raise HTTPException(status_code=404, detail="One or both roles not found")

    context = {
        "roles": [
            {"title": a.title, "automation_pct": a.automation_pct,
             "augmentation_pct": a.augmentation_pct, "confidence": a.confidence,
             "future_role_profile": a.future_role_profile},
            {"title": b.title, "automation_pct": b.automation_pct,
             "augmentation_pct": b.augmentation_pct, "confidence": b.confidence,
             "future_role_profile": b.future_role_profile},
        ]
    }
    narrative = generate_narrative(
        f"Compare the future AI impact on a {a.title} versus a {b.title}.", context
    )

    return {"role_a": a, "role_b": b, "narrative": narrative}
