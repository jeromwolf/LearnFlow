from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.content import (
    Content, Section, Course, Category, UserContentProgress
)
from app.schemas.content import (
    ContentCreate, ContentUpdate,
    SectionCreate, SectionUpdate,
    CourseCreate, CourseUpdate,
    CategoryCreate, CategoryUpdate,
    UserContentProgressCreate, UserContentProgressUpdate
)

# Content CRUD operations
def get_content(db: Session, content_id: int) -> Optional[Content]:
    return db.query(Content).filter(Content.id == content_id).first()

def get_contents(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    content_type: Optional[str] = None,
    is_published: Optional[bool] = None,
    creator_id: Optional[int] = None,
    section_id: Optional[int] = None,
) -> List[Content]:
    query = db.query(Content)
    
    if content_type:
        query = query.filter(Content.content_type == content_type)
    if is_published is not None:
        query = query.filter(Content.is_published == is_published)
    if creator_id is not None:
        query = query.filter(Content.creator_id == creator_id)
    if section_id is not None:
        query = query.filter(Content.section_id == section_id)
    
    return query.offset(skip).limit(limit).all()

def create_content(db: Session, content: ContentCreate, creator_id: int) -> Content:
    db_content = Content(**content.model_dump(), creator_id=creator_id)
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

def update_content(
    db: Session, db_content: Content, content_update: ContentUpdate
) -> Content:
    update_data = content_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_content, field, value)
    
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

def delete_content(db: Session, content_id: int) -> bool:
    db_content = get_content(db, content_id)
    if not db_content:
        return False
    
    db.delete(db_content)
    db.commit()
    return True

# Section CRUD operations
def get_section(db: Session, section_id: int) -> Optional[Section]:
    return db.query(Section).filter(Section.id == section_id).first()

def get_sections(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    course_id: Optional[int] = None,
) -> List[Section]:
    query = db.query(Section)
    
    if course_id is not None:
        query = query.filter(Section.course_id == course_id)
    
    return query.order_by(Section.order, Section.id).offset(skip).limit(limit).all()

def create_section(db: Session, section: SectionCreate) -> Section:
    db_section = Section(**section.model_dump())
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

def update_section(
    db: Session, db_section: Section, section_update: SectionUpdate
) -> Section:
    update_data = section_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_section, field, value)
    
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

def delete_section(db: Session, section_id: int) -> bool:
    db_section = get_section(db, section_id)
    if not db_section:
        return False
    
    db.delete(db_section)
    db.commit()
    return True

# Course CRUD operations
def get_course(db: Session, course_id: int) -> Optional[Course]:
    return db.query(Course).filter(Course.id == course_id).first()

def get_courses(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_published: Optional[bool] = None,
    instructor_id: Optional[int] = None,
    category_id: Optional[int] = None,
) -> List[Course]:
    query = db.query(Course)
    
    if is_published is not None:
        query = query.filter(Course.is_published == is_published)
    if instructor_id is not None:
        query = query.filter(Course.instructor_id == instructor_id)
    if category_id is not None:
        query = query.join(Course.categories).filter(Category.id == category_id)
    
    return query.offset(skip).limit(limit).all()

def create_course(db: Session, course: CourseCreate) -> Course:
    db_course = Course(**course.model_dump(exclude={"category_ids"}))
    
    if hasattr(course, 'category_ids') and course.category_ids:
        categories = db.query(Category).filter(Category.id.in_(course.category_ids)).all()
        db_course.categories = categories
    
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def update_course(
    db: Session, db_course: Course, course_update: CourseUpdate
) -> Course:
    update_data = course_update.model_dump(exclude_unset=True)
    
    # Update categories if provided
    if 'category_ids' in update_data:
        category_ids = update_data.pop('category_ids', [])
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        db_course.categories = categories
    
    # Update other fields
    for field, value in update_data.items():
        setattr(db_course, field, value)
    
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def delete_course(db: Session, course_id: int) -> bool:
    db_course = get_course(db, course_id)
    if not db_course:
        return False
    
    db.delete(db_course)
    db.commit()
    return True

# Category CRUD operations
def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()

def get_categories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[int] = None,
) -> List[Category]:
    query = db.query(Category)
    
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    else:
        query = query.filter(Category.parent_id.is_(None))
    
    return query.offset(skip).limit(limit).all()

def create_category(db: Session, category: CategoryCreate) -> Category:
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(
    db: Session, db_category: Category, category_update: CategoryUpdate
) -> Category:
    update_data = category_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> bool:
    db_category = get_category(db, category_id)
    if not db_category:
        return False
    
    # Check if category has children
    children_count = db.query(Category).filter(Category.parent_id == category_id).count()
    if children_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a category with subcategories"
        )
    
    db.delete(db_category)
    db.commit()
    return True

# User Content Progress CRUD operations
def get_user_content_progress(
    db: Session, user_id: int, content_id: int
) -> Optional[UserContentProgress]:
    return db.query(UserContentProgress).filter(
        UserContentProgress.user_id == user_id,
        UserContentProgress.content_id == content_id
    ).first()

def get_user_contents_progress(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    is_completed: Optional[bool] = None,
) -> List[UserContentProgress]:
    query = db.query(UserContentProgress).filter(
        UserContentProgress.user_id == user_id
    )
    
    if is_completed is not None:
        query = query.filter(UserContentProgress.is_completed == is_completed)
    
    return query.offset(skip).limit(limit).all()

def create_user_content_progress(
    db: Session, user_id: int, progress: UserContentProgressCreate
) -> UserContentProgress:
    # Check if content exists
    content = get_content(db, progress.content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check if progress already exists
    db_progress = get_user_content_progress(db, user_id, progress.content_id)
    if db_progress:
        return update_user_content_progress(db, db_progress, progress)
    
    # Create new progress
    progress_data = progress.model_dump()
    progress_data["user_id"] = user_id
    
    db_progress = UserContentProgress(**progress_data)
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

def update_user_content_progress(
    db: Session,
    db_progress: UserContentProgress,
    progress_update: UserContentProgressUpdate,
) -> UserContentProgress:
    update_data = progress_update.model_dump(exclude_unset=True)
    
    # Update progress
    for field, value in update_data.items():
        setattr(db_progress, field, value)
    
    # Update timestamps
    if 'is_completed' in update_data and update_data['is_completed']:
        if not db_progress.completed_at:
            db_progress.completed_at = db.func.now()
    
    if not db_progress.started_at:
        db_progress.started_at = db.func.now()
    
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

def delete_user_content_progress(
    db: Session, user_id: int, content_id: int
) -> bool:
    db_progress = get_user_content_progress(db, user_id, content_id)
    if not db_progress:
        return False
    
    db.delete(db_progress)
    db.commit()
    return True
