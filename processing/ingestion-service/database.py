from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, BigInteger, JSON, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import config

# Create SQLAlchemy engine
engine = create_engine(config.DATABASE_URL)
metadata = MetaData()

# Define datasets table
datasets = Table(
    config.DATASET_TABLE,
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(255), nullable=False),
    Column("file_path", String(512), nullable=False),
    Column("file_type", String(50), nullable=False),
    Column("file_size", BigInteger, nullable=False),
    Column("created_at", TIMESTAMP, server_default=func.now()),
    Column("metadata", JSON),
)

# Create declarative base
Base = declarative_base()

# Define Dataset ORM model
class Dataset(Base):
    __tablename__ = config.DATASET_TABLE

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    metadata = Column(JSON)

    def __repr__(self):
        return f"<Dataset(id={self.id}, name='{self.name}', type='{self.file_type}')>"


# Create tables if they don't exist
def init_db():
    Base.metadata.create_all(engine)
