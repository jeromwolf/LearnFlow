from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Any

from app.core.database import supabase
from app.core.security import (
    create_access_token,
    get_current_user,
    verify_password,
    get_password_hash,
    UserInToken,
    TokenData
)
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """
    새로운 사용자를 등록합니다.
    
    - **user**: 등록할 사용자 정보 (이메일, 사용자명, 비밀번호)
    """
    try:
        # 이메일 중복 확인
        existing_user = supabase.table("users").select("*").eq("email", user.email).execute()
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일 주소입니다."
            )
        
        # 사용자명 중복 확인
        existing_username = supabase.table("users").select("*").eq("username", user.username).execute()
        if existing_username.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 사용자명입니다."
            )
        
        # 비밀번호 해시 생성
        hashed_password = get_password_hash(user.password)
        
        # Supabase Auth에 사용자 등록
        auth_response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "username": user.username,
                    "full_name": user.full_name or "",
                    "avatar_url": user.avatar_url or ""
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 등록에 실패했습니다."
            )
        
        # 사용자 정보 반환 (비밀번호 제외)
        return {
            "id": auth_response.user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "is_active": True,
            "is_superuser": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 등록 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    사용자 로그인 및 액세스 토큰 발급
    
    - **username**: 사용자 이메일
    - **password**: 비밀번호
    """
    try:
        # 사용자 인증
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 액세스 토큰 생성
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": auth_response.user.id, "email": auth_response.user.email},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "username": auth_response.user.user_metadata.get("username", ""),
                "full_name": auth_response.user.user_metadata.get("full_name", ""),
                "avatar_url": auth_response.user.user_metadata.get("avatar_url", ""),
                "is_superuser": False  # 실제로는 사용자 역할에 따라 설정
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserInToken = Depends(get_current_user)):
    """
    현재 인증된 사용자 정보를 가져옵니다.
    """
    try:
        # Supabase에서 사용자 정보 조회
        user = supabase.auth.get_user(current_user.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
            
        return {
            "id": user.id,
            "email": user.email,
            "username": user.user_metadata.get("username", ""),
            "full_name": user.user_metadata.get("full_name", ""),
            "avatar_url": user.user_metadata.get("avatar_url", ""),
            "is_active": True,
            "is_superuser": False,  # 실제로는 사용자 역할에 따라 설정
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 정보를 불러오는 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/refresh-token", response_model=Token)
async def refresh_token(current_user: UserInToken = Depends(get_current_user)):
    """
    액세스 토큰을 갱신합니다.
    """
    try:
        # 새 액세스 토큰 발급
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user.user_id, "email": current_user.email},
            expires_delta=access_token_expires
        )
        
        # 사용자 정보 조회
        user = supabase.auth.get_user(current_user.user_id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.user_metadata.get("username", ""),
                "full_name": user.user_metadata.get("full_name", ""),
                "avatar_url": user.user_metadata.get("avatar_url", ""),
                "is_superuser": False  # 실제로는 사용자 역할에 따라 설정
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 갱신에 실패했습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout")
async def logout(current_user: UserInToken = Depends(get_current_user)):
    """
    사용자 로그아웃 (클라이언트에서 토큰 삭제)
    """
    try:
        # Supabase Auth에서 로그아웃
        supabase.auth.sign_out()
        return {"message": "성공적으로 로그아웃되었습니다."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그아웃 중 오류가 발생했습니다: {str(e)}"
        )
