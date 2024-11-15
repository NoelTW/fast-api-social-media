import databases
import sqlalchemy

from config import config


# Create all tables
metadata = sqlalchemy.MetaData()

post_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
)

comment_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id"), nullable=False),
)


# Create database object
engine = sqlalchemy.create_engine(
    url=config.DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata.create_all(engine)

databae = databases.Database(
    url=config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLLBACK
)
