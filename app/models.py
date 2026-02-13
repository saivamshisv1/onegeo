from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from .database import Base


class WellLogFile(Base):
    __tablename__ = "well_log_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_path = Column(String, nullable=False)
    s3_key = Column(String, nullable=True)
    min_depth = Column(Float, nullable=False)
    max_depth = Column(Float, nullable=False)
    curves = Column(JSON, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    points = relationship("WellLogPoint", back_populates="log_file", cascade="all, delete-orphan")


class WellLogPoint(Base):
    __tablename__ = "well_log_points"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("well_log_files.id", ondelete="CASCADE"), nullable=False, index=True)
    depth = Column(Float, nullable=False, index=True)
    values = Column(JSON, nullable=False)

    log_file = relationship("WellLogFile", back_populates="points")
