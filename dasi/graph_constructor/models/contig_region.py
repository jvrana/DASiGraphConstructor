from copy import deepcopy

from dasi.graph_constructor.exceptions import ContigError
from dasi.graph_constructor.models.region import Region


class ContigRegion(Region):
    """ A ContigRegion is a :class:`Region` designated for establishing SUBJECTS or QUERIES from BLAST results. Circular
    topologies are supported. Contig regions support gaps. """

    START_INDEX = 1  # Convention is carried over from BLAST results, BE CAREFUL!
    NEW_PRIMER = "new_primer"
    DIRECT_END = "direct"
    DEFAULT_END = NEW_PRIMER

    def __init__(self, start, end, context, name="", forward=True, sequence=None, filename=None):
        """
        Constructs a new :class:`ContigRegion`

        :param start: start of the region
        :type start: int
        :param end: end of the region
        :type end: int
        :param context: the context for the region
        :type context: Context
        :param name: optional name of the region
        :type name: str
        :param forward: direction of the region
        :type forward: boolean
        :param sequence: optional sequence of the region
        :type sequence: str
        :param filename: optional filename of the region
        :type filename: str
        """
        direction = Region.FORWARD
        if not forward:
            direction = Region.REVERSE
        super(ContigRegion, self).__init__(start, end, context, direction=direction, name=name)
        self.sequence = sequence
        self.filename = filename

        # @staticmethod
        # def create_from_dictionary(**kwargs):
        #     """
        #     BLAST specific method for creating contigs
        #
        #     :param kwargs:
        #     :type kwargs:
        #     :return:
        #     :rtype:
        #     """
        #     new = ContigRegion(kwargs['s_end'], kwargs['subject_length'], kwargs['subject_circular'], kwargs['s_start'],
        #                        forward=kwargs['subject_strand'] == 'plus', sequence=kwargs['subject_seq'])
        #     return new

    # @property
    # def length(self):
    #     """ Returns the length of the associated sequence (including gaps), else returns the span from start to end
    #     indices """
    #     if self.sequence:
    #         return len(self.sequence)
    #     else:
    #         return super(ContigRegion, self).length

    def reverse_direction(self):
        """Reverses the direction of the contig"""
        if self.sequence:
            self.sequence = self.sequence[::-1]
        return super(ContigRegion, self).reverse_direction()

    def copy(self):
        """Makes an approximately identical copy of the contig"""
        return deepcopy(self)
        # return ContigRegion(self.start, self.end,
        #              forward=(self.direction == Region.FORWARD),
        #              context=self.context,
        #              sequence=self.sequence,
        #              filename=self.filename,
        #              name=self.name)

    def fuse(self, other, inplace=False):
        """
        Concatenates two regions together.

        :param other: the region to fuse
        :type other: ContigRegion
        :param inplace: whether to return a copy
        :type inplace: boolean
        :return: the fused region. If with_copy is True, then the new region will
                be a copy of the region.
        :raises ContigError: if one region has a sequence and the other does not
        """
        if type(self) != type(other):
            raise ContigError("Cannot fuse. ContigRegions must be of same type!")
        s1, s2 = self.sequence, other.sequence
        f = super(ContigRegion, self).fuse(other)
        if f:
            if s1 and s2:
                f.sequence = s1 + s2
            elif s1 or s2:
                raise ContigError("Cannot fuse ContigRegions when one has a sequence and the other does not.")
        return f