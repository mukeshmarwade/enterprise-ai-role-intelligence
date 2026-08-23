from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Role
from backend.schemas import RankingResponse
from backend.llm import generate_narrative

router = APIRouter(prefix="/api/rank", tags=["rank"])


@router.get("", response_model=RankingResponse)
def top_impacted_roles(
    n: int = Query(5, ge=1, le=24, description="How many top roles to return"),
    db: Session = Depends(get_db),
):
    roles = db.query(Role).all()
    ranked = sorted(
        roles,
        key=lambda r: (r.automation_pct + r.augmentation_pct),
        reverse=True,
    )[:n]

    top_roles = [
        {
            "title": r.title,
            "change_score": round(r.automation_pct + r.augmentation_pct, 1),
            "automation_pct": r.automation_pct,
            "augmentation_pct": r.augmentation_pct,
            "confidence": r.confidence,
        }
        for r in ranked
    ]

    context = {"roles": [
        {"title": r.title, "automation_pct": r.automation_pct,
         "augmentation_pct": r.augmentation_pct, "confidence": r.confidence}
        for r in ranked
    ]}
    narrative = generate_narrative(
        f"Which {n} roles are likely to experience the greatest AI-driven change, and why?", context
    )

    return {"top_roles": top_roles, "narrative": narrative}
