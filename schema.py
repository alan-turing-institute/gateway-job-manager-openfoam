from database import db
from uuid import uuid4
from sqlalchemy_utils import ArrowType


class Template(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    source_uri = db.Column(db.String)
    destination_path = db.Column(db.String)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    job = db.relationship("Job", back_populates="templates")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.source_uri == other.source_uri and
                    self.destination_path == other.destination_path
                    )
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __lt__(self, other):
        # Need to support < operator for sorting
        if isinstance(other, self.__class__):
            # We have no strong view of a canonical sort order but do want to
            # be able to sort consistently to allow comparison of lists so we
            # just sort by hash, which hashes all fields used for equality
            # checking
            return self.__hash__() < other.__hash__()
        return NotImplemented

    def __hash__(self):
        return hash((self.source_uri, self.destination_path))
