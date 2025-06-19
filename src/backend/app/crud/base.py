"""
CRUD (Create, Read, Update, Delete) 연산을 위한 기본 클래스입니다.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """CRUD 기본 클래스"""

    def __init__(self, model: Type[ModelType]):
        """CRUD 객체 초기화"""
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """ID로 단일 항목 조회"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[ModelType]:
        """여러 항목 조회 (페이징 처리)"""
        query = db.query(self.model)
        
        # 필터링 조건 적용
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """새 항목 생성"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """기존 항목 업데이트"""
        obj_data = jsonable_encoder(db_obj)
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """ID로 항목 삭제"""
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def count(self, db: Session, **kwargs) -> int:
        """조건에 맞는 항목 수 조회"""
        query = db.query(self.model)
        
        # 필터링 조건 적용
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        
        return query.count()

    def exists(self, db: Session, **kwargs) -> bool:
        """조건에 맞는 항목이 존재하는지 확인"""
        query = db.query(self.model)
        
        # 필터링 조건 적용
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        
        return query.first() is not None
