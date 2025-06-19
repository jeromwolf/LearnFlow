from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.user import UserInToken
from app import schemas, crud

router = APIRouter()

# Content endpoints
@router.post("/contents/", response_model=schemas.Content, status_code=status.HTTP_201_CREATED)
def create_content(
    content: schemas.ContentCreate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    새로운 콘텐츠를 생성합니다.
    """
    return crud.create_content(db=db, content=content, creator_id=current_user.id)

@router.get("/contents/", response_model=List[schemas.Content])
def read_contents(
    skip: int = 0,
    limit: int = 100,
    content_type: Optional[str] = None,
    is_published: Optional[bool] = None,
    creator_id: Optional[int] = None,
    section_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    콘텐츠 목록을 조회합니다.
    """
    contents = crud.get_contents(
        db,
        skip=skip,
        limit=limit,
        content_type=content_type,
        is_published=is_published,
        creator_id=creator_id,
        section_id=section_id,
    )
    return contents

@router.get("/contents/{content_id}", response_model=schemas.Content)
def read_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    특정 콘텐츠를 조회합니다.
    """
    db_content = crud.get_content(db, content_id=content_id)
    if db_content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return db_content

@router.put("/contents/{content_id}", response_model=schemas.Content)
def update_content(
    content_id: int,
    content: schemas.ContentUpdate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    콘텐츠를 업데이트합니다.
    """
    db_content = crud.get_content(db, content_id=content_id)
    if db_content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # 작성자 또는 관리자만 수정 가능
    if db_content.creator_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this content"
        )
    
    return crud.update_content(db=db, db_content=db_content, content_update=content)

@router.delete("/contents/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    콘텐츠를 삭제합니다.
    """
    db_content = crud.get_content(db, content_id=content_id)
    if db_content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # 작성자 또는 관리자만 삭제 가능
    if db_content.creator_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this content"
        )
    
    crud.delete_content(db=db, content_id=content_id)
    return None

# Section endpoints
@router.post("/sections/", response_model=schemas.Section, status_code=status.HTTP_201_CREATED)
def create_section(
    section: schemas.SectionCreate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    새로운 섹션을 생성합니다.
    """
    # 강의 소유자인지 확인
    course = crud.get_course(db, course_id=section.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create a section in this course"
        )
    
    return crud.create_section(db=db, section=section)

@router.get("/sections/", response_model=List[schemas.Section])
def read_sections(
    skip: int = 0,
    limit: int = 100,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    섹션 목록을 조회합니다.
    """
    return crud.get_sections(db, skip=skip, limit=limit, course_id=course_id)

@router.get("/sections/{section_id}", response_model=schemas.Section)
def read_section(
    section_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    특정 섹션을 조회합니다.
    """
    db_section = crud.get_section(db, section_id=section_id)
    if db_section is None:
        raise HTTPException(status_code=404, detail="Section not found")
    return db_section

@router.put("/sections/{section_id}", response_model=schemas.Section)
def update_section(
    section_id: int,
    section: schemas.SectionUpdate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    섹션을 업데이트합니다.
    """
    db_section = crud.get_section(db, section_id=section_id)
    if db_section is None:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # 강의 소유자 또는 관리자만 수정 가능
    course = crud.get_course(db, course_id=db_section.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this section"
        )
    
    return crud.update_section(db=db, db_section=db_section, section_update=section)

@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(
    section_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    섹션을 삭제합니다.
    """
    db_section = crud.get_section(db, section_id=section_id)
    if db_section is None:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # 강의 소유자 또는 관리자만 삭제 가능
    course = crud.get_course(db, course_id=db_section.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this section"
        )
    
    crud.delete_section(db=db, section_id=section_id)
    return None

# Course endpoints
@router.post("/courses/", response_model=schemas.Course, status_code=status.HTTP_201_CREATED)
def create_course(
    course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    새로운 강의를 생성합니다.
    """
    # 강사 또는 관리자만 강의 생성 가능
    if not current_user.is_instructor and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors can create courses"
        )
    
    # 강사 ID 설정
    course.instructor_id = current_user.id
    
    return crud.create_course(db=db, course=course)

@router.get("/courses/", response_model=List[schemas.Course])
def read_courses(
    skip: int = 0,
    limit: int = 100,
    is_published: Optional[bool] = None,
    instructor_id: Optional[int] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    강의 목록을 조회합니다.
    """
    # 관리자가 아니면 공개된 강의만 조회 가능
    if not current_user.is_superuser and not current_user.is_instructor:
        is_published = True
    
    return crud.get_courses(
        db,
        skip=skip,
        limit=limit,
        is_published=is_published,
        instructor_id=instructor_id,
        category_id=category_id,
    )

@router.get("/courses/{course_id}", response_model=schemas.Course)
def read_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    특정 강의를 조회합니다.
    """
    db_course = crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 강의가 비공개인 경우 강사 또는 관리자만 접근 가능
    if not db_course.is_published and db_course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This course is not published"
        )
    
    return db_course

@router.put("/courses/{course_id}", response_model=schemas.Course)
def update_course(
    course_id: int,
    course: schemas.CourseUpdate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    강의를 업데이트합니다.
    """
    db_course = crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 강사 또는 관리자만 수정 가능
    if db_course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this course"
        )
    
    # 강사 ID는 변경 불가
    if hasattr(course, 'instructor_id') and course.instructor_id != db_course.instructor_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change course instructor"
        )
    
    return crud.update_course(db=db, db_course=db_course, course_update=course)

@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    강의를 삭제합니다.
    """
    db_course = crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 강사 또는 관리자만 삭제 가능
    if db_course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this course"
        )
    
    crud.delete_course(db=db, course_id=course_id)
    return None

# Category endpoints
@router.post("/categories/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    새로운 카테고리를 생성합니다. (관리자 전용)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create categories"
        )
    
    return crud.create_category(db=db, category=category)

@router.get("/categories/", response_model=List[schemas.Category])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    카테고리 목록을 조회합니다.
    """
    return crud.get_categories(db, skip=skip, limit=limit, parent_id=parent_id)

@router.put("/categories/{category_id}", response_model=schemas.Category)
def update_category(
    category_id: int,
    category: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    카테고리를 업데이트합니다. (관리자 전용)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update categories"
        )
    
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return crud.update_category(db=db, db_category=db_category, category_update=category)

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    카테고리를 삭제합니다. (관리자 전용)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete categories"
        )
    
    crud.delete_category(db=db, category_id=category_id)
    return None

# User Content Progress endpoints
@router.get("/user-progress/", response_model=List[schemas.UserContentProgress])
def read_user_contents_progress(
    skip: int = 0,
    limit: int = 100,
    is_completed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    사용자의 콘텐츠 학습 진행 상황을 조회합니다.
    """
    return crud.get_user_contents_progress(
        db, user_id=current_user.id, skip=skip, limit=limit, is_completed=is_completed
    )

@router.get("/user-progress/{content_id}", response_model=schemas.UserContentProgress)
def read_user_content_progress(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    특정 콘텐츠에 대한 사용자의 학습 진행 상황을 조회합니다.
    """
    db_progress = crud.get_user_content_progress(db, user_id=current_user.id, content_id=content_id)
    if db_progress is None:
        raise HTTPException(status_code=404, detail="Progress not found")
    return db_progress

@router.post("/user-progress/", response_model=schemas.UserContentProgress, status_code=status.HTTP_201_CREATED)
def create_user_content_progress(
    progress: schemas.UserContentProgressCreate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    콘텐츠 학습 진행 상황을 생성하거나 업데이트합니다.
    """
    return crud.create_user_content_progress(
        db=db, user_id=current_user.id, progress=progress
    )

@router.put("/user-progress/{content_id}", response_model=schemas.UserContentProgress)
def update_user_content_progress(
    content_id: int,
    progress: schemas.UserContentProgressUpdate,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    콘텐츠 학습 진행 상황을 업데이트합니다.
    """
    db_progress = crud.get_user_content_progress(db, user_id=current_user.id, content_id=content_id)
    if db_progress is None:
        raise HTTPException(status_code=404, detail="Progress not found")
    
    return crud.update_user_content_progress(
        db=db, db_progress=db_progress, progress_update=progress
    )

@router.delete("/user-progress/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_content_progress(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user),
):
    """
    콘텐츠 학습 진행 상황을 삭제합니다.
    """
    crud.delete_user_content_progress(db=db, user_id=current_user.id, content_id=content_id)
    return None
