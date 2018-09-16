import itertools
import uuid
from copy import deepcopy

from dasi.graph_constructor.exceptions import ContigError
from dasi.graph_constructor.models.contig_region import ContigRegion


# TODO: make a special class for contigs that contain all the weird methods (like divide contig) in a separate Class or
# TODO: Somehow lock subject and queries together?

class Contig(object):
    """
    A Contig represents a relationship between two :class:`ContigRegion` of DNA.

    Abstractly, a contig is a relationship between a QUERY and SUBJECT. A query sequence may
    have many alignments to many subjects. There alignments are represented by a "Contig."
    Contains a query region (the thing aligned to the subject) and a subject region.
    Circular topologies are supported.

    Contig Features:
        * unique contig_id
        * type of contig (str)
        * type of "end" for fragments

    """
    gid = 0

    # TODO: Decorate entire class with something that asserts subject and query always have the same length
    def __init__(self, query, subject, contig_type, **meta):
        """
        Contig constructor. Takes a query and subject :class:`ContigRegion` and a contig type
        to specify the nature of the relationship. Additional metadata may be attached.

        :param query: query region
        :type query: ContigRegion
        :param subject: subject region
        :type subject: ContigRegion
        :param contig_type: the type of contig
        :type contig_type: str
        :param meta: additional metadata
        :type meta: dict
        """
        vars(self).update(locals())
        self.query = self.query.copy()
        self.subject = self.subject.copy()
        self.contig_type = contig_type
        self.contig_id = None
        self._assign_id()
        self.quality = 1.0  # used for future machine learning / AI
        self._validate_regions()
        self._check_types()
        self.metadata = meta

    # TODO: pyblast parses regions incorrectly
    @staticmethod
    def _validate_regions_helper(region1, region2, msg=None):
        """
        Validates that two regions have the same length

        :param region1: first region
        :param region2: second region to compare
        :return: None
        :raises ContigError: if first and second region have different lenghts
        """
        if msg is None:
            msg = "Region1 and Region2 must have same region spans (R1Spanc: {0}, R2Span: {1})".format(
                region1.length,
                region2.length
            )
            msg += "\nQuery: {}".format(region1)
            msg += "\nSubject: {}".format(region2)
        if region1.length != region2.length:
            raise ContigError(msg)

    def _validate_regions(self, msg=None):
        """
        Validates that the query and subject of this contig remain the same

        :param msg: message to raise for possible exception
        :return: None
        :raises ContigError: if query and subject have different lengths
        """
        if msg is None:
            msg = "Query and subject must have same region spans (QSpan: {0}, SSpan: {1})".format(
                self.query.length,
                self.subject.length
            )
            msg += "\nQuery: {}".format(self.query)
            msg += "\nSubject: {}".format(self.subject)
        self._validate_regions_helper(self.query, self.subject, msg=msg)

    def _check_types(self):
        """Validates that query and subject are ContigRegions"""
        qtype = type(self.query)
        stype = type(self.subject)
        msg = ""
        if not isinstance(self.query, ContigRegion):
            msg += f"Query must be a ContigRegion but is a {qtype}"
        if not isinstance(self.subject, ContigRegion):
            msg += f" Subject must be a ContigRegion but is a {stype}"
        if msg:
            raise ContigError(msg)

    @property
    def alignment_length(self):
        """
        Returns the length of the query

        :return: the length of the query
        """
        self._validate_regions()
        return self.query.length

    @classmethod
    def _modify_end(cls, new_end_pos, reg1, reg2):
        """
        Modify the ends of the query and subject so that their lengths
        remain the same.

        :param new_end_pos: new end position
        :type new_end_pos: int
        :param reg1: a region
        :type reg1: ContigRegion
        :param reg2: a region to compare
        :type reg2: ContigRegion
        :return:
        """
        if not isinstance(new_end_pos, int):
            raise ValueError("End position must be an Int")
        diff = new_end_pos - reg1.end
        if reg1.is_reverse():
            diff *= -1
        reg1.extend_end(diff)
        reg2.extend_end(diff)
        cls._validate_regions_helper(reg1, reg2)

    @classmethod
    def _modify_start(cls, new_start_pos, reg1, reg2):
        """
        Modify the start of two regions so that their lengths remain
        the same.

        :param new_start_pos: new start position
        :param reg1: a region
        :type reg1: ContigRegion
        :param reg2: a region to compare
        :type reg2: ContigRegion
        :return:
        """
        if not isinstance(new_start_pos, int):
            raise ValueError("Start position must be an Int")
        diff = new_start_pos - reg1.start
        if reg1.is_forward():
            diff *= -1
        reg1.extend_start(diff)
        reg2.extend_start(diff)
        cls._validate_regions_helper(reg1, reg2)

    def modify_query_start(self, x):
        """Modify the query start position"""
        self._modify_start(x, self.query, self.subject)

    def modify_query_end(self, x):
        """Modify the query end position"""
        self._modify_end(x, self.query, self.subject)

    def modify_subject_start(self, x):
        """Modify the subject start position"""
        self._modify_start(x, self.subject, self.query)

    def modify_subject_end(self, x):
        """Modify the subject end position"""
        self._modify_end(x, self.subject, self.query)

    def modify_query(self, s, e):
        """Modify the start and end positions for the query"""
        self.modify_query_start(s)
        self.modify_query_end(e)

    def modify_subject(self, s, e):
        """Modify the start and end positions for the subject"""
        self.modify_subject_start(s)
        self.modify_subject_end(e)

    def modify_query_ends(self, left_end, right_end):
        if self.query.left_end == self.query.start:
            self.modify_query(left_end, right_end)
        elif self.query.right_end == self.query.start:
            self.modify_query(right_end, left_end)
        else:
            raise ContigError("Starts and ends of query are not equal to either left_end or right_end")

    def _assign_id(self):
        """Assign a unique id to this contig"""
        self.contig_id = self.gid
        self.__class__.gid += 1

    def copy(self):
        """returns a deepcopy"""
        c = deepcopy(self)
        c._assign_id()
        return c
        # return Contig(
        #     self.query.copy(),
        #     self.subject.copy(),
        #     self.contig_type,
        #     **self.metadata
        # )

    def same_context(self, other):
        """ Returns True if self.query and other.query AND self.subject and other.subject have the same context. """
        return self.query.same_context(other.query) and \
               self.subject.same_context(other.subject)

    def reverse_direction(self):
        """Reverses direction of the query and subject"""
        self.query.reverse_direction()
        self.subject.reverse_direction()

    def fuse(self, other):
        """Fuses the query and subject together with another :class:`ContigRegion`"""
        if self.same_context(other):
            self.query.fuse(other.query)
            self.subject.fuse(other.subject)
        else:
            raise ContigError("Cannot fuse contigs that have different contexts.")

    # TODO: should this be new *subject*??
    def sub_query(self, start, end):
        """
        Creates a sub query at new start and end

        :param start: new start position for query
        :type start: int
        :param end: new end position for query
        :type end: int
        :return: new BlastContig
        :rtype: BlastCongi
        :raises ContigError: if start or end not withing query region
        """
        if not self.query.within_region(start):
            raise ContigError("Cannot break, start position {0} is not within query {1}".format(start, self.query))
        if not self.query.within_region(end):
            raise ContigError("Cannot break, end position {0} is not within query {1}".format(end, self.query))
        new_contig = self.copy()
        new_contig.modify_query(start, end)
        return new_contig

    #
    # def create_sub_queries(self, starts, ends):
    #     positions = list(itertools.product(starts, ends))
    #
    # def is_direct(self):
    #     pass
    #

    # TODO: what is 'circular' used for?
    def divide_contig(self, starts, ends, include_self=True, contig_type=None, circular=None):
        """
        Divide a contig into every possible contig from a list of starts and ends (as in primers)

        e.g. ::

            OLD                |--------------------------------|
            Points                (x)>      <   >
                               |-----|
                                  (x)|------|
                                            |---|
                                                |----------------|
                                            |--------------------|
                                  (x)|---------------------------|
                               |---------------------------------|     <<< if include_contig == True
                                  (x)|----------|
                               |------------|

        :param starts: list of start positions (using query)
        :param ends: list of end positions (using query)
        :param include_contig: include self return list
        :param contig_type: type of contigs to return
        :param circular: whether to
        :return:
        """

        contigs = []
        starts.append(self.query.start)
        ends.append(self.query.end)

        for s, e in itertools.product(starts, ends):
            new_contig = self.sub_query(s, e)
            contigs.append(new_contig)

        # include self
        if include_self:
            contigs.append(self)

        # change contig_type
        if contig_type is not None:
            for c in contigs:
                c.contig_type = contig_type

        return contigs

    def __len__(self):
        return self.alignment_length

    def __repr__(self):
        return "Contig({} Q{}-{}, S{}-{})".format(
            self.contig_id,
            self.query.start,
            self.query.end,
            self.subject.start,
            self.subject.end)

    def __copy__(self):
        return self.copy()
