from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, BigInteger, NUMERIC, JSON, MetaData, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import config

# Create SQLAlchemy engine
engine = create_engine(config.DATABASE_URL)
metadata = MetaData()

# Define datasets table reference
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

# Define assessments table
assessments = Table(
    config.ASSESSMENT_TABLE,
    metadata,
    Column("id", Integer, primary_key=True),
    Column("dataset_id", Integer, ForeignKey(f"{config.DATASET_TABLE}.id")),
    Column("module", String(50), nullable=False),
    Column("criterion", String(50), nullable=False),
    Column("score", NUMERIC(3, 1), nullable=False),  # Score from 0.0 to 10.0
    Column("details", JSON),
    Column("created_at", TIMESTAMP, server_default=func.now()),
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

# Define Assessment ORM model
class Assessment(Base):
    __tablename__ = config.ASSESSMENT_TABLE

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey(f"{config.DATASET_TABLE}.id"))
    module = Column(String(50), nullable=False)
    criterion = Column(String(50), nullable=False)
    score = Column(NUMERIC(3, 1), nullable=False)  # Score from 0.0 to 10.0
    details = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<Assessment(id={self.id}, dataset_id={self.dataset_id}, module='{self.module}', criterion='{self.criterion}', score={self.score})>"

# Create tables if they don't exist
def init_db():
    # Create only the assessments table (dataset table is created by ingestion service)
    assessments.create(engine, checkfirst=True)
