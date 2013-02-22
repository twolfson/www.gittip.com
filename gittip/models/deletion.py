from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Text, TIMESTAMP

from gittip.orm import db

class Deletion(db.Model):
    __tablename__ = 'deletions'

    id = Column(Integer, nullable=False, primary_key=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False,
                       default="now()")
    deleted_was = Column(Text, nullable=False)
    archived_as = Column(Text, ForeignKey("participants.id",
                                          onupdate="RESTRICT",
                                          ondelete="RESTRICT"), nullable=False)
