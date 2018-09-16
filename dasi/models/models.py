from sqlalchemy import Column, Integer, Text, Float,  String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from dasi.database import Model


class Sequence(Model.Base):
    __tablename__ = 'sequence'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    circular = Column(Boolean, nullable=False, default=False)
    bases = Column(Text)
    size = Column(Integer)
    description = Column(Text)
    features = relationship("Feature", back_populates="sequence")


class Feature(Model.Base):
    __tablename__ = 'feature'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)
    strand = Column(Integer, nullable=False)
    sequence_id = Column(Integer, ForeignKey('sequence.id'), nullable=False)
    sequence = relationship("Sequence", back_populates="features")


class Primer(Model.Base):
    __tablename__ = "primer"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    bases = Column(Text, nullable=False)


# TODO: basically the output of a pyblast result
class SequenceRegion(Model.Base):
    __tablename__ = "sequence_region"
    id = Column(Integer, primary_key=True)
    sequence_id = Column(Integer, ForeignKey('sequence.id'), nullable=False)
    sequence = relationship("Sequence")
    length = Column(Integer, nullable=False)
    name = Column(Text)
    circular = Column(Boolean, nullable=False)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)
    strand = Column(String, nullable=False)
    bases = Column(Text, nullable=False)


class AlignmentScore(Model.Base):
    __tablename__ = "alignment_score"
    id = Column(Integer, primary_key=True)
    alignment = relationship("Alignment", uselist=False, back_populates="alignment_score")
    score = Column(Float, nullable=False)
    evalue = Column(Float, nullable=False)
    bit_score = Column(Float, nullable=False)
    identical = Column(Integer, nullable=False)
    gaps_open = Column(Integer, nullable=False)
    gaps = Column(Integer, nullable=False)
    alignment_length = Column(Integer, nullable=False)
    span_origin = Column(Boolean)


class Alignment(Model.Base):
    __tablename__ = "alignment"
    id = Column(Integer, primary_key=True)

    query_id = Column(Integer, ForeignKey('sequence_region.id'), nullable=False)
    query = relationship("SequenceRegion", foreign_keys=[query_id])

    subject_id = Column(Integer, ForeignKey('sequence_region.id'), nullable=False)
    subject = relationship("SequenceRegion", foreign_keys=[subject_id])

    alignment_score_id = Column(Integer, ForeignKey('alignment_score.id'), nullable=False)
    alignment_score = relationship("AlignmentScore", back_populates="alignment")
#
#
# class QueryAlignment(Model.Base):
#     __tablename__ = "query"
#
#
# class Alignment(Model.Base):
#     __tablename__ = "alignment"
#     id = Column(Integer, primary_key=True)
#
