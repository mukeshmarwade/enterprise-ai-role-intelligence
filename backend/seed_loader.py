import json

from backend.database import SessionLocal, engine, Base
from backend.models import Role, Activity
from backend.scoring import score_role, build_future_role_profile
from backend.config import SEED_FILE


def load_seed(reset: bool = False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if reset:
            db.query(Activity).delete()
            db.query(Role).delete()
            db.commit()

        if db.query(Role).count() > 0:
            print("Roles already loaded — skipping (use reset=True to reload).")
            return

        with open(SEED_FILE) as f:
            roles_data = json.load(f)

        for r in roles_data:
            role_score = score_role(r["activities"])
            narrative = build_future_role_profile(
                r["role"], role_score, r["new_responsibilities"], r["future_skills"]
            )

            role = Role(
                title=r["role"],
                level=r["level"],
                industry="Finance",
                processes=r["processes"],
                current_skills=r["current_skills"],
                ai_exposure_today=r["ai_exposure_today"],
                new_responsibilities=r["new_responsibilities"],
                future_skills=r["future_skills"],
                automation_pct=role_score.automation_pct,
                augmentation_pct=role_score.augmentation_pct,
                unaffected_pct=role_score.unaffected_pct,
                confidence=role_score.confidence,
                future_role_profile=narrative,
                reason_codes=role_score.reason_codes,
            )
            db.add(role)
            db.flush()  # get role.id

            for a_in, a_scored in zip(r["activities"], role_score.activity_scores):
                db.add(Activity(
                    role_id=role.id,
                    name=a_scored.name,
                    weight=a_in.get("weight", 0),
                    structured=a_in.get("structured", False),
                    repetitive=a_in.get("repetitive", False),
                    rule_based=a_in.get("rule_based", False),
                    requires_judgment=a_in.get("requires_judgment", False),
                    requires_creativity=a_in.get("requires_creativity", False),
                    interpersonal=a_in.get("interpersonal", False),
                    automation_score=a_scored.automation_score,
                    augmentation_score=a_scored.augmentation_score,
                    classification=a_scored.classification,
                    reason=a_scored.reason,
                ))

        db.commit()
        print(f"Seeded {len(roles_data)} roles.")
    finally:
        db.close()


if __name__ == "__main__":
    load_seed(reset=True)
