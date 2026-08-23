from typing import List, Optional
from pydantic import BaseModel


class ActivityOut(BaseModel):
    name: str
    weight: float
    automation_score: float
    augmentation_score: float
    classification: str
    reason: str

    class Config:
        from_attributes = True


class RoleSummary(BaseModel):
    id: int
    title: str
    level: str
    automation_pct: float
    augmentation_pct: float
    unaffected_pct: float
    confidence: str

    class Config:
        from_attributes = True


class RoleDetail(BaseModel):
    id: int
    title: str
    level: str
    industry: str
    processes: List[str]
    current_skills: List[str]
    ai_exposure_today: Optional[str]
    new_responsibilities: List[str]
    future_skills: List[str]
    automation_pct: float
    augmentation_pct: float
    unaffected_pct: float
    confidence: str
    future_role_profile: Optional[str]
    reason_codes: List[str]
    activities: List[ActivityOut]

    class Config:
        from_attributes = True


class ComparisonResponse(BaseModel):
    role_a: RoleDetail
    role_b: RoleDetail
    narrative: str


class RankingItem(BaseModel):
    title: str
    change_score: float  # automation_pct + augmentation_pct (total disruption)
    automation_pct: float
    augmentation_pct: float
    confidence: str


class RankingResponse(BaseModel):
    top_roles: List[RankingItem]
    narrative: str
