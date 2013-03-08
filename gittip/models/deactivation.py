from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Text, TIMESTAMP

from gittip.orm import db

class Deactivation(db.Model):
    __tablename__ = 'deactivations'

    id = Column(Integer, nullable=False, primary_key=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False,
                       default="now()")
    deactivated_was = Column(Text, nullable=False)
    archived_as = Column(Text, ForeignKey("participants.id",
                                          onupdate="RESTRICT",
                                          ondelete="RESTRICT"), nullable=False)
