from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_moderation import crud_moderation
from app.models.user import User
from app.schemas.moderation import (
    ReportResponse,
    ReportUpdateStatus,
    ModerationQueueResponse,
    BulkActionRequest,
    BannedWordCreate,
    BannedWordResponse,
)

router = APIRouter()

VALID_REPORT_STATUSES = {"pending", "reviewed", "resolved", "dismissed"}


@router.get("/reports", summary="List reports (MODERATOR+)")
def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user("MODERATOR")),
) -> Any:
    if status and status not in VALID_REPORT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(VALID_REPORT_STATUSES)}",
        )
    reports, total = crud_moderation.get_reports(db, skip=skip, limit=limit, status_filter=status)
    items = [ReportResponse.model_validate(r) for r in reports]
    return {"status": "success", "data": {"items": items, "total": total}}


@router.patch("/reports/{report_id}", summary="Update report status (MODERATOR+)")
def update_report_status(
    report_id: int,
    data: ReportUpdateStatus,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user("MODERATOR")),
) -> Any:
    valid_update_statuses = {"reviewed", "resolved", "dismissed"}
    if data.status not in valid_update_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_update_statuses)}",
        )

    report = crud_moderation.get_report(db, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    updated = crud_moderation.update_report_status(
        db, report_id=report_id, status=data.status, reviewed_by=current_user.id
    )
    return {"status": "success", "data": ReportResponse.model_validate(updated)}


@router.get("/queue", summary="Combined moderation queue (MODERATOR+)")
def get_moderation_queue(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user("MODERATOR")),
) -> Any:
    queue = crud_moderation.get_moderation_queue(db, skip=skip, limit=limit)
    items = [ModerationQueueResponse.model_validate(item) for item in queue]
    return {"status": "success", "data": {"items": items, "total": len(items)}}


@router.post("/bulk", summary="Bulk process reports (ADMIN+)")
def bulk_process(
    data: BulkActionRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user("ADMIN")),
) -> Any:
    try:
        count = crud_moderation.bulk_process(
            db, ids=data.ids, action=data.action, admin_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "success", "data": {"processed": count}}


@router.get("/banned-words", summary="List banned words (MODERATOR+)")
def list_banned_words(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user("MODERATOR")),
) -> Any:
    words = crud_moderation.get_banned_words(db)
    items = [BannedWordResponse.model_validate(w) for w in words]
    return {"status": "success", "data": {"items": items, "total": len(items)}}


@router.post("/banned-words", summary="Add banned word (ADMIN+)", status_code=201)
def create_banned_word(
    data: BannedWordCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user("ADMIN")),
) -> Any:
    word = crud_moderation.create_banned_word(
        db, word=data.word, created_by=current_user.id
    )
    return {"status": "success", "data": BannedWordResponse.model_validate(word)}


@router.delete("/banned-words/{word_id}", summary="Delete banned word (ADMIN+)")
def delete_banned_word(
    word_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user("ADMIN")),
) -> Any:
    word = crud_moderation.delete_banned_word(db, word_id=word_id)
    if not word:
        raise HTTPException(status_code=404, detail="Banned word not found")
    return {"status": "success", "data": BannedWordResponse.model_validate(word)}
