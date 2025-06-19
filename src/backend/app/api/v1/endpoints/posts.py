from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.core.database import supabase
from app.core.security import get_current_user
from app.schemas.post import (
    Post, PostCreate, PostUpdate, PostListResponse, PostSortBy
)
from app.schemas.comment import CommentListResponse
from app.schemas.like import LikeStatus
from app.schemas.bookmark import BookmarkStatus

router = APIRouter()

# 게시글 목록 조회
@router.get("/", response_model=PostListResponse)
async def read_posts(
    board_id: Optional[int] = Query(None, description="게시판 ID (필터링용)"),
    sort_by: PostSortBy = Query(PostSortBy.LATEST, description="정렬 기준"),
    keyword: Optional[str] = Query(None, description="검색 키워드 (제목+내용)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    current_user: dict = Depends(get_current_user)
):
    """
    게시글 목록을 조회합니다.
    
    - **board_id**: 특정 게시판의 게시글만 필터링
    - **sort_by**: 정렬 기준 (latest, popular, comments, likes, views)
    - **keyword**: 제목 또는 내용에 키워드가 포함된 게시글 검색
    - **page**: 페이지 번호 (1부터 시작)
    - **limit**: 페이지당 항목 수 (최대 100)
    """
    try:
        # 기본 쿼리 구성
        query = supabase.table("posts").select("*")
        
        # 게시판 필터링
        if board_id is not None:
            query = query.eq("board_id", board_id)
            
            # 게시판 존재 여부 확인
            board = supabase.table("boards").select("*").eq("id", board_id).execute()
            if not board.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ID가 {board_id}인 게시판을 찾을 수 없습니다."
                )
        
        # 삭제된 게시글 제외
        query = query.eq("is_deleted", False)
        
        # 키워드 검색
        if keyword:
            query = query.or_(f"title.ilike.%{keyword}%,content.ilike.%{keyword}%")
        
        # 정렬 기준 적용
        if sort_by == PostSortBy.LATEST:
            query = query.order("created_at", desc=True)
        elif sort_by == PostSortBy.POPULAR:
            query = query.order("view_count", desc=True).order("created_at", desc=True)
        elif sort_by == PostSortBy.COMMENTS:
            # 댓글 많은 순 (서브쿼리 필요 - Supabase에서는 제한적 지원)
            query = query.order("comment_count", desc=True).order("created_at", desc=True)
        elif sort_by == PostSortBy.LIKES:
            # 좋아요 많은 순 (서브쿼리 필요 - Supabase에서는 제한적 지원)
            query = query.order("like_count", desc=True).order("created_at", desc=True)
        elif sort_by == PostSortBy.VIEWS:
            query = query.order("view_count", desc=True).order("created_at", desc=True)
        
        # 총 개수 조회
        count_query = query.select("id", count="exact")
        count_result = count_query.execute()
        total = count_result.count or 0
        
        # 페이징 처리
        start = (page - 1) * limit
        end = start + limit - 1
        
        # 데이터 조회
        response = query.range(start, end).execute()
        
        # 사용자 좋아요 및 북마크 상태 확인 (선택적)
        posts = response.data
        if current_user and posts:
            post_ids = [post["id"] for post in posts]
            
            # 좋아요 상태 확인
            likes = supabase.table("post_likes")\
                .select("post_id")\
                .in_("post_id", post_ids)\
                .eq("user_id", current_user.user_id)\
                .execute()
            
            liked_post_ids = {like["post_id"] for like in likes.data}
            
            # 북마크 상태 확인
            bookmarks = supabase.table("bookmarks")\
                .select("post_id")\
                .in_("post_id", post_ids)\
                .eq("user_id", current_user.user_id)\
                .execute()
                
            bookmarked_post_ids = {bookmark["post_id"] for bookmark in bookmarks.data}
            
            # 상태 정보 추가
            for post in posts:
                post["is_liked"] = post["id"] in liked_post_ids
                post["is_bookmarked"] = post["id"] in bookmarked_post_ids
        
        return {
            "total": total,
            "items": posts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시글 목록을 불러오는 중 오류가 발생했습니다: {str(e)}"
        )

# 게시글 상세 조회
@router.get("/{post_id}", response_model=Post)
async def read_post(
    post_id: int = Path(..., description="게시글 ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    게시글 상세 정보를 조회합니다.
    
    - **post_id**: 조회할 게시글 ID
    """
    try:
        # 게시글 조회
        response = supabase.table("posts").select("*").eq("id", post_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {post_id}인 게시글을 찾을 수 없습니다."
            )
            
        post = response.data[0]
        
        # 삭제된 게시글인 경우
        if post.get("is_deleted", False):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="삭제된 게시글입니다."
            )
        
        # 조회수 증가 (비동기로 처리하는 것이 좋음)
        supabase.table("posts")\
            .update({"view_count": post["view_count"] + 1})\
            .eq("id", post_id)\
            .execute()
        
        post["view_count"] += 1
        
        # 작성자 정보 조회 (예시: Supabase Auth 사용 시)
        if "user_id" in post:
            try:
                user = supabase.auth.admin.get_user_by_id(post["user_id"]).user
                if user:
                    post["author"] = {
                        "id": user.id,
                        "email": user.email,
                        "username": user.user_metadata.get("username", ""),
                        "avatar_url": user.user_metadata.get("avatar_url")
                    }
            except Exception:
                pass
        
        # 좋아요 및 북마크 상태 확인
        if current_user:
            # 좋아요 상태 확인
            like = supabase.table("post_likes")\
                .select("id")\
                .eq("post_id", post_id)\
                .eq("user_id", current_user.user_id)\
                .execute()
            
            post["is_liked"] = len(like.data) > 0
            
            # 북마크 상태 확인
            bookmark = supabase.table("bookmarks")\
                .select("id")\
                .eq("post_id", post_id)\
                .eq("user_id", current_user.user_id)\
                .execute()
                
            post["is_bookmarked"] = len(bookmark.data) > 0
        
        return post
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시글을 불러오는 중 오류가 발생했습니다: {str(e)}"
        )

# 새 게시글 작성
@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    새 게시글을 작성합니다.
    
    - **post**: 작성할 게시글 정보
    """
    try:
        # 게시판 존재 여부 확인
        board = supabase.table("boards").select("*").eq("id", post.board_id).execute()
        if not board.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {post.board_id}인 게시판을 찾을 수 없습니다."
            )
        
        # 게시글 데이터 준비
        post_data = post.dict()
        post_data["user_id"] = current_user.user_id
        
        # 게시글 생성
        response = supabase.table("posts").insert(post_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="게시글 생성에 실패했습니다."
            )
        
        # 게시판의 게시글 수 증가
        supabase.table("boards")\
            .update({"post_count": (board.data[0].get("post_count", 0) + 1)})\
            .eq("id", post.board_id)\
            .execute()
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시글 작성 중 오류가 발생했습니다: {str(e)}"
        )

# 게시글 수정
@router.put("/{post_id}", response_model=Post)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    게시글을 수정합니다. (작성자 또는 관리자만 가능)
    
    - **post_id**: 수정할 게시글 ID
    - **post_update**: 수정할 게시글 정보
    """
    try:
        # 게시글 존재 여부 확인
        response = supabase.table("posts").select("*").eq("id", post_id).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {post_id}인 게시글을 찾을 수 없습니다."
            )
            
        post = response.data[0]
        
        # 권한 확인 (작성자 또는 관리자)
        if post["user_id"] != current_user.user_id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시글 수정 권한이 없습니다."
            )
        
        # 업데이트할 데이터 준비 (None이 아닌 필드만 포함)
        update_data = {k: v for k, v in post_update.dict().items() if v is not None}
        if not update_data:
            return post
            
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # 게시글 업데이트
        response = supabase.table("posts")\
            .update(update_data)\
            .eq("id", post_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="게시글 수정에 실패했습니다."
            )
            
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시글 수정 중 오류가 발생했습니다: {str(e)}"
        )

# 게시글 삭제
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    게시글을 삭제합니다. (작성자 또는 관리자만 가능)
    
    - **post_id**: 삭제할 게시글 ID
    """
    try:
        # 게시글 존재 여부 확인
        response = supabase.table("posts").select("*").eq("id", post_id).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {post_id}인 게시글을 찾을 수 없습니다."
            )
            
        post = response.data[0]
        
        # 권한 확인 (작성자 또는 관리자)
        if post["user_id"] != current_user.user_id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시글 삭제 권한이 없습니다."
            )
        
        # 게시글 삭제 (논리적 삭제)
        update_data = {
            "is_deleted": True,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("posts")\
            .update(update_data)\
            .eq("id", post_id)\
            .execute()
        
        # 게시판의 게시글 수 감소
        if post.get("board_id"):
            board = supabase.table("boards").select("*").eq("id", post["board_id"]).execute()
            if board.data:
                post_count = max(0, board.data[0].get("post_count", 1) - 1)
                supabase.table("boards")\
                    .update({"post_count": post_count})\
                    .eq("id", post["board_id"])\
                    .execute()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시글 삭제 중 오류가 발생했습니다: {str(e)}"
        )

# 게시글 좋아요 토글
@router.post("/{post_id}/like", response_model=LikeStatus)
async def toggle_post_like(
    post_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    게시글 좋아요를 토글합니다.
    
    - **post_id**: 좋아요를 토글할 게시글 ID
    """
    try:
        # 게시글 존재 여부 확인
        post = supabase.table("posts").select("*").eq("id", post_id).execute()
        if not post.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {post_id}인 게시글을 찾을 수 없습니다."
            )
        
        # 이미 좋아요를 눌렀는지 확인
        like = supabase.table("post_likes")\
            .select("*")\
            .eq("post_id", post_id)\
            .eq("user_id", current_user.user_id)\
            .execute()
        
        is_liked = False
        
        if like.data:
            # 좋아요 취소
            supabase.table("post_likes")\
                .delete()\
                .eq("id", like.data[0]["id"])\
                .execute()
            
            # 좋아요 수 감소
            supabase.table("posts")\
                .update({"like_count": post.data[0].get("like_count", 1) - 1})\
                .eq("id", post_id)\
                .execute()
            
            is_liked = False
        else:
            # 좋아요 추가
            supabase.table("post_likes")\
                .insert({
                    "post_id": post_id,
                    "user_id": current_user.user_id
                })\
                .execute()
            
            # 좋아요 수 증가
            supabase.table("posts")\
                .update({"like_count": post.data[0].get("like_count", 0) + 1})\
                .eq("id", post_id)\
                .execute()
            
            is_liked = True
        
        # 최신 좋아요 수 조회
        updated_post = supabase.table("posts").select("like_count").eq("id", post_id).execute()
        like_count = updated_post.data[0].get("like_count", 0) if updated_post.data else 0
        
        return {
            "is_liked": is_liked,
            "like_count": like_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"좋아요 처리 중 오류가 발생했습니다: {str(e)}"
        )

# 게시글 북마크 토글
@router.post("/{post_id}/bookmark", response_model=BookmarkStatus)
async def toggle_post_bookmark(
    post_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    게시글 북마크를 토글합니다.
    
    - **post_id**: 북마크를 토글할 게시글 ID
    """
    try:
        # 게시글 존재 여부 확인
        post = supabase.table("posts").select("*").eq("id", post_id).execute()
        if not post.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {post_id}인 게시글을 찾을 수 없습니다."
            )
        
        # 이미 북마크를 했는지 확인
        bookmark = supabase.table("bookmarks")\
            .select("*")\
            .eq("post_id", post_id)\
            .eq("user_id", current_user.user_id)\
            .execute()
        
        is_bookmarked = False
        
        if bookmark.data:
            # 북마크 삭제
            supabase.table("bookmarks")\
                .delete()\
                .eq("id", bookmark.data[0]["id"])\
                .execute()
            
            is_bookmarked = False
        else:
            # 북마크 추가
            supabase.table("bookmarks")\
                .insert({
                    "post_id": post_id,
                    "user_id": current_user.user_id
                })\
                .execute()
            
            is_bookmarked = True
        
        return {
            "is_bookmarked": is_bookmarked
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"북마크 처리 중 오류가 발생했습니다: {str(e)}"
        )

# 게시글의 댓글 목록 조회
@router.get("/{post_id}/comments", response_model=CommentListResponse)
async def read_post_comments(
    post_id: int,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    current_user: dict = Depends(get_current_user)
):
    """
    게시글의 댓글 목록을 조회합니다.
    
    - **post_id**: 댓글을 조회할 게시글 ID
    - **page**: 페이지 번호 (1부터 시작)
    - **limit**: 페이지당 항목 수 (최대 100)
    """
    try:
        # 게시글 존재 여부 확인
        post = supabase.table("posts").select("id").eq("id", post_id).execute()
        if not post.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {post_id}인 게시글을 찾을 수 없습니다."
            )
        
        # 댓글 조회 (부모 댓글만 먼저 조회)
        query = supabase.table("comments")\
            .select("*")\
            .eq("post_id", post_id)\
            .is_("parent_id", None)\
            .eq("is_deleted", False)\
            .order("created_at", desc=False)  # 오래된 순으로 정렬
        
        # 총 개수 조회
        count_query = query.select("id", count="exact")
        count_result = count_query.execute()
        total = count_result.count or 0
        
        # 페이징 처리
        start = (page - 1) * limit
        end = start + limit - 1
        
        # 데이터 조회
        response = query.range(start, end).execute()
        comments = response.data
        
        # 대댓글 조회 및 매핑
        if comments:
            # 부모 댓글 ID 목록
            parent_ids = [comment["id"] for comment in comments]
            
            # 대댓글 조회
            replies = supabase.table("comments")\
                .select("*")\
                .in_("parent_id", parent_ids)\
                .eq("is_deleted", False)\
                .order("created_at", desc=False)\
                .execute()
            
            # 대댓글을 부모 댓글에 매핑
            replies_by_parent = {}
            for reply in replies.data:
                parent_id = reply["parent_id"]
                if parent_id not in replies_by_parent:
                    replies_by_parent[parent_id] = []
                replies_by_parent[parent_id].append(reply)
            
            # 댓글에 대댓글 추가
            for comment in comments:
                comment["replies"] = replies_by_parent.get(comment["id"], [])
        
        # 사용자 좋아요 상태 확인 (선택적)
        if current_user and comments:
            # 모든 댓글 ID 수집 (부모 + 대댓글)
            all_comment_ids = [comment["id"] for comment in comments]
            for comment in comments:
                all_comment_ids.extend([reply["id"] for reply in comment.get("replies", [])])
            
            # 좋아요 상태 확인
            if all_comment_ids:
                likes = supabase.table("comment_likes")\
                    .select("comment_id")\
                    .in_("comment_id", all_comment_ids)\
                    .eq("user_id", current_user.user_id)\
                    .execute()
                
                liked_comment_ids = {like["comment_id"] for like in likes.data}
                
                # 댓글과 대댓글에 좋아요 상태 추가
                for comment in comments:
                    comment["is_liked"] = comment["id"] in liked_comment_ids
                    for reply in comment.get("replies", []):
                        reply["is_liked"] = reply["id"] in liked_comment_ids
        
        return {
            "total": total,
            "items": comments
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 목록을 불러오는 중 오류가 발생했습니다: {str(e)}"
        )
