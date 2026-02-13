from fastapi import APIRouter

router = APIRouter(prefix="/manage/health")


@router.get("", status_code=200)
def ping() -> None:
    return
