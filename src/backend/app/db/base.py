"""
SQLAlchemy Base class and metadata definition.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

# Define naming convention for constraints
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=convention)

# Create base class for models
Base = declarative_base(metadata=metadata)

__all__ = ['Base', 'metadata']
