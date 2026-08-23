from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Role
from backend.schemas import RoleSummary, RoleDetail

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.get("", response_model=List[RoleSummary])
def list_roles(
    db: Session = Depends(get_db),
    level: Optional[str] = Query(None, description="Filter by level e.g. Analyst, Manager, Executive"),
    search: Optional[str] = Query(None, description="Search role titles"),
):
    q = db.query(Role)
    if level:
        q = q.filter(Role.level == level)
    if search:
        q = q.filter(Role.title.ilike(f"%{search}%"))
    return q.order_by(Role.title).all()


@router.get("/{role_id}", response_model=RoleDetail)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role
