from sqlalchemy import (
    MetaData,
    Integer,
    String,
    ForeignKey,
    Table,
    Column,
    TIMESTAMP,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime


metadata = MetaData()

# Description of the user table model
user = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False, unique=True),
    Column("password", String, nullable=False),
    Column("email", String, nullable=False, unique=True),
    Column("registered", TIMESTAMP, default=datetime.utcnow, nullable=False),
)

# Description of the model table posts
post = Table(
    "post",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("posted_username", String, ForeignKey("users.username")),
    Column("title", String),
    Column("body", String),
    Column("posted_at", TIMESTAMP, default=datetime.utcnow),
)

reactions = Table(
    "likes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("reaction", Integer, nullable=False, default=False),
    Column("post_id", Integer, ForeignKey("post.id"), nullable=False, default=False),
    Column("reactkey", String, unique=True),
)
