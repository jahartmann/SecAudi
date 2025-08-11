from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from .database import Base


class Server(Base):
    __tablename__ = "servers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    host = Column(String)
    ssh_key = Column(Text, nullable=True)

    audits = relationship("Audit", back_populates="server")


class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    rating = Column(String)
    report_markdown = Column(Text)
    scorecard_json = Column(Text)

    server = relationship("Server", back_populates="audits")
