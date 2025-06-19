from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.core.database import supabase
from app.schemas.board import Board, BoardCreate, BoardUpdate, BoardInDBBase
from app.core.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Board])
async def read_boards(
    skip: int = 0, 
    limit: int = 100,
    is_active: Optional[bool] = None
):
    """
    게시판 목록을 조회합니다.
    
    - **skip**: 건너뛸 레코드 수 (기본값: 0)
    - **limit**: 반환할 최대 레코드 수 (기본값: 100, 최대: 100)
    - **is_active**: 활성화된 게시판만 조회 (기본값: None, 전체 조회)
    """
    try:
        query = supabase.table("boards").select("*")
        
        # 활성화 여부 필터링
        if is_active is not None:
            query = query.eq("is_active", is_active)
            
        # 정렬 (생성일자 내림차순)
        query = query.order("created_at", desc=True)
        
        # 페이징 처리
        response = query.range(skip, skip + limit - 1).execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시판 목록을 불러오는 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{board_id}", response_model=Board)
async def read_board(board_id: int):
    """
    특정 게시판의 상세 정보를 조회합니다.
    
    - **board_id**: 조회할 게시판 ID
    """
    try:
        response = supabase.table("boards").select("*").eq("id", board_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {board_id}인 게시판을 찾을 수 없습니다."
            )
            
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시판 정보를 불러오는 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/", response_model=Board, status_code=status.HTTP_201_CREATED)
async def create_board(
    board: BoardCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    새 게시판을 생성합니다. (관리자만 가능)
    
    - **board**: 생성할 게시판 정보
    """
    # 관리자 권한 확인
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시판 생성을 위한 권한이 없습니다."
        )
    
    try:
        # 중복 이름 확인
        existing = supabase.table("boards").select("*").eq("name", board.name).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{board.name}' 이름의 게시판이 이미 존재합니다."
            )
        
        # 게시판 생성
        response = supabase.table("boards").insert(board.dict()).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="게시판 생성에 실패했습니다."
            )
            
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시판 생성 중 오류가 발생했습니다: {str(e)}"
        )

@router.put("/{board_id}", response_model=Board)
async def update_board(
    board_id: int,
    board_update: BoardUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    게시판 정보를 수정합니다. (관리자만 가능)
    
    - **board_id**: 수정할 게시판 ID
    - **board_update**: 수정할 게시판 정보
    """
    # 관리자 권한 확인
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시판 수정을 위한 권한이 없습니다."
        )
    
    try:
        # 게시판 존재 여부 확인
        existing = supabase.table("boards").select("*").eq("id", board_id).execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {board_id}인 게시판을 찾을 수 없습니다."
            )
        
        # 업데이트할 데이터 준비 (None이 아닌 필드만 포함)
        update_data = {k: v for k, v in board_update.dict().items() if v is not None}
        if not update_data:
            return existing.data[0]
            
        # 게시판 업데이트
        response = supabase.table("boards").update(update_data).eq("id", board_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="게시판 수정에 실패했습니다."
            )
            
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시판 수정 중 오류가 발생했습니다: {str(e)}"
        )

@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    게시판을 삭제합니다. (관리자만 가능)
    
    - **board_id**: 삭제할 게시판 ID
    """
    # 관리자 권한 확인
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시판 삭제를 위한 권한이 없습니다."
        )
    
    try:
        # 게시판 존재 여부 확인
        existing = supabase.table("boards").select("*").eq("id", board_id).execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {board_id}인 게시판을 찾을 수 없습니다."
            )
        
        # 게시판 삭제
        response = supabase.table("boards").delete().eq("id", board_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="게시판 삭제에 실패했습니다."
            )
            
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시판 삭제 중 오류가 발생했습니다: {str(e)}"
        )
