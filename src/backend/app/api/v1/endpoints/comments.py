from fastapi import APIRouter, Depends, HTTPException, status, Path, Body, Query
from typing import List, Optional
from datetime import datetime

from app.core.database import supabase
from app.core.security import get_current_user
from app.schemas.comment import Comment, CommentCreate, CommentUpdate, CommentListResponse
from app.schemas.like import LikeStatus

router = APIRouter()

# 새 댓글 작성
@router.post("/", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: CommentCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    새 댓글을 작성합니다.
    
    - **comment**: 작성할 댓글 정보
    """
    try:
        # 게시글 존재 여부 확인
        post = supabase.table("posts").select("id").eq("id", comment.post_id).execute()
        if not post.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {comment.post_id}인 게시글을 찾을 수 없습니다."
            )
        
        # 부모 댓글 확인 (대댓글인 경우)
        if comment.parent_id:
            parent_comment = supabase.table("comments").select("id").eq("id", comment.parent_id).execute()
            if not parent_comment.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ID가 {comment.parent_id}인 부모 댓글을 찾을 수 없습니다."
                )
        
        # 댓글 데이터 준비
        comment_data = comment.dict()
        comment_data["user_id"] = current_user.user_id
        
        # 댓글 생성
        response = supabase.table("comments").insert(comment_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="댓글 작성에 실패했습니다."
            )
        
        # 게시글의 댓글 수 증가
        supabase.table("posts")\
            .update({"comment_count": post.data[0].get("comment_count", 0) + 1})\
            .eq("id", comment.post_id)\
            .execute()
        
        # 부모 댓글이 있는 경우, 부모 댓글의 대댓글 수 증가
        if comment.parent_id:
            supabase.table("comments")\
                .update({"reply_count": parent_comment.data[0].get("reply_count", 0) + 1})\
                .eq("id", comment.parent_id)\
                .execute()
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 작성 중 오류가 발생했습니다: {str(e)}"
        )

# 댓글 수정
@router.put("/{comment_id}", response_model=Comment)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    댓글을 수정합니다. (작성자 또는 관리자만 가능)
    
    - **comment_id**: 수정할 댓글 ID
    - **comment_update**: 수정할 댓글 내용
    """
    try:
        # 댓글 존재 여부 확인
        response = supabase.table("comments").select("*").eq("id", comment_id).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {comment_id}인 댓글을 찾을 수 없습니다."
            )
            
        comment = response.data[0]
        
        # 권한 확인 (작성자 또는 관리자)
        if comment["user_id"] != current_user.user_id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="댓글 수정 권한이 없습니다."
            )
        
        # 댓글 수정
        update_data = comment_update.dict()
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("comments")\
            .update(update_data)\
            .eq("id", comment_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="댓글 수정에 실패했습니다."
            )
            
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 수정 중 오류가 발생했습니다: {str(e)}"
        )

# 댓글 삭제
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    댓글을 삭제합니다. (작성자 또는 관리자만 가능)
    
    - **comment_id**: 삭제할 댓글 ID
    """
    try:
        # 댓글 존재 여부 확인
        response = supabase.table("comments").select("*").eq("id", comment_id).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {comment_id}인 댓글을 찾을 수 없습니다."
            )
            
        comment = response.data[0]
        
        # 권한 확인 (작성자 또는 관리자)
        if comment["user_id"] != current_user.user_id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="댓글 삭제 권한이 없습니다."
            )
        
        # 댓글 삭제 (논리적 삭제)
        update_data = {
            "is_deleted": True,
            "content": "삭제된 댓글입니다.",
            "updated_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("comments")\
            .update(update_data)\
            .eq("id", comment_id)\
            .execute()
        
        # 게시글의 댓글 수 감소
        supabase.table("posts")\
            .update({"comment_count": comment.get("comment_count", 1) - 1})\
            .eq("id", comment["post_id"])\
            .execute()
        
        # 부모 댓글이 있는 경우, 부모 댓글의 대댓글 수 감소
        if comment.get("parent_id"):
            supabase.table("comments")\
                .update({"reply_count": comment.get("reply_count", 1) - 1})\
                .eq("id", comment["parent_id"])\
                .execute()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 삭제 중 오류가 발생했습니다: {str(e)}"
        )

# 댓글 좋아요 토글
@router.post("/{comment_id}/like", response_model=LikeStatus)
async def toggle_comment_like(
    comment_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    댓글 좋아요를 토글합니다.
    
    - **comment_id**: 좋아요를 토글할 댓글 ID
    """
    try:
        # 댓글 존재 여부 확인
        comment = supabase.table("comments").select("*").eq("id", comment_id).execute()
        if not comment.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {comment_id}인 댓글을 찾을 수 없습니다."
            )
        
        # 이미 좋아요를 눌렀는지 확인
        like = supabase.table("comment_likes")\
            .select("*")\
            .eq("comment_id", comment_id)\
            .eq("user_id", current_user.user_id)\
            .execute()
        
        is_liked = False
        
        if like.data:
            # 좋아요 취소
            supabase.table("comment_likes")\
                .delete()\
                .eq("id", like.data[0]["id"])\
                .execute()
            
            # 좋아요 수 감소
            supabase.table("comments")\
                .update({"like_count": comment.data[0].get("like_count", 1) - 1})\
                .eq("id", comment_id)\
                .execute()
            
            is_liked = False
        else:
            # 좋아요 추가
            supabase.table("comment_likes")\
                .insert({
                    "comment_id": comment_id,
                    "user_id": current_user.user_id
                })\
                .execute()
            
            # 좋아요 수 증가
            supabase.table("comments")\
                .update({"like_count": comment.data[0].get("like_count", 0) + 1})\
                .eq("id", comment_id)\
                .execute()
            
            is_liked = True
        
        # 최신 좋아요 수 조회
        updated_comment = supabase.table("comments").select("like_count").eq("id", comment_id).execute()
        like_count = updated_comment.data[0].get("like_count", 0) if updated_comment.data else 0
        
        return {
            "is_liked": is_liked,
            "like_count": like_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 좋아요 처리 중 오류가 발생했습니다: {str(e)}"
        )

# 사용자별 댓글 목록 조회
@router.get("/user/{user_id}", response_model=CommentListResponse)
async def read_user_comments(
    user_id: str,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    current_user: dict = Depends(get_current_user)
):
    """
    특정 사용자가 작성한 댓글 목록을 조회합니다.
    
    - **user_id**: 댓글을 조회할 사용자 ID
    - **page**: 페이지 번호 (1부터 시작)
    - **limit**: 페이지당 항목 수 (최대 100)
    """
    try:
        # 사용자 존재 여부 확인 (간단하게 댓글 존재 여부로 대체)
        user_comments = supabase.table("comments").select("id").eq("user_id", user_id).limit(1).execute()
        if not user_comments.data:
            return {"total": 0, "items": []}
        
        # 댓글 조회
        query = supabase.table("comments")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("is_deleted", False)\
            .order("created_at", desc=True)
        
        # 총 개수 조회
        count_query = query.select("id", count="exact")
        count_result = count_query.execute()
        total = count_result.count or 0
        
        # 페이징 처리
        start = (page - 1) * limit
        end = start + limit - 1
        
        # 데이터 조회
        response = query.range(start, end).execute()
        
        # 게시글 제목 추가
        comments = response.data
        if comments:
            post_ids = list({comment["post_id"] for comment in comments})
            posts = supabase.table("posts").select("id,title").in_("id", post_ids).execute()
            
            post_title_map = {post["id"]: post["title"] for post in posts.data}
            
            for comment in comments:
                comment["post_title"] = post_title_map.get(comment["post_id"], "")
        
        return {
            "total": total,
            "items": comments
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 댓글 목록을 불러오는 중 오류가 발생했습니다: {str(e)}"
        )
