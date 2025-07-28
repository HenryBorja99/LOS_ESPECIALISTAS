from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    email = Column(String)
    telefono = Column(String)
    archivo = Column(String)
    fecha_subida = Column(DateTime, default=datetime.utcnow)

# Base de datos SQLite
engine = create_engine("sqlite:///data/candidatos.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
