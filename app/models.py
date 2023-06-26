from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.sql.expression import null
from .database import Base
from . import models
from .database import engine

models.Base.metadata.create_all(bind=engine)


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, default=True)
