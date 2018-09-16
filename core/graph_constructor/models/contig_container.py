# from .contig import *
import itertools
import os

from core.graph_constructor.exceptions import ContigContainerError, ContigError
from core.graph_constructor.models.blast_contig import *
from core.graph_constructor.utils import pseudocircularize, pair
from collections import MutableMapping
import warnings
from Bio import BiopythonWarning
warnings.simplefilter('ignore', BiopythonWarning)


class ContigContainer(MutableMapping):
    """A Container for :class:`Contigs`"""

    def __init__(self, contigs=None, sequences=None):
        """
        :class:`ContigContainer` constructor

        :param contigs: list of Contigs
        :type contigs: list
        """
        if contigs is None:
            contigs = []
        self.__contig_dictionary = {x.contig_id: x for x in contigs}
        seq_dict = {}
        if sequences:
            seq_dict = {seq['id']: seq for seq in sequences}
        self.seq_dict = seq_dict
        self._filter = None
        self._sort_filter = lambda x: x.query.start

    def set_filter(self, f):
        """
        Assigns a filter to this contig container.

        :param f:
        :type f:
        :return:
        :rtype:
        """
        raise NotImplementedError
        self._filter = f

    def set_sort_filter(self, f):
        """
        Sets the sort filter at self._sort_filter.

        :param f: filter function
        :type f: function or lambda
        :return: None
        :rtype: None
        """
        self._sort_filter = f

    def sorted_contigs(self, reverse=False):
        """
        Returns the list of sorted contigs (based on self._sort_filter)

        :param reverse: if true, reverses the list
        :type reverse: boolean
        :return: list of contigs sorted by self._sort_filter
        :rtype: list
        """
        contigs = self.contigs
        return sorted(contigs, key=self._sort_filter, reverse=reverse)

    @property
    def contigs(self):
        """
        Returns the list of contigs

        :return: list of contigs
        :rtype: list
        """
        return list(self.__contig_dictionary.values())

    # @classmethod
    # def find_alignments(cls, templates_directory, query_path, force_linear=False):
    #     """
    #
    #     :param templates_directory: path to the directory containing template sequences
    #     :type templates_directory: basestring
    #     :param query_path: path to the query sequence
    #     :type query_path: basestring
    #     :param force_linear: if true, a pseudocircularized sequence for the query will not be created
    #     :type force_linear: boolean
    #     :return:
    #     :rtype:
    #     """
    #     if not force_linear:
    #         if PySequence.dna_at_path_is_circular(query_path):
    #             tokens = os.path.basename(query_path).split('.')
    #             dirname = os.path.dirname(query_path)
    #
    #             outpath = os.path.join(dirname, f"{tokens[0]}_pseudocircular.{tokens[1]}")
    #             pseudocircularize(query_path, outpath)
    #             query_path = outpath
    #     aligner = Aligner('db', templates_directory, query_path)
    #     aligner.quick_blastn()
    #
    #     return cls.parse_blast_results(aligner.results,
    #                                    sequences=aligner.seq_db.sequences)

    # :    @classmethod
    # def find_perfect_alignments(cls)

    @classmethod
    def parse_alignments(cls, pyblast_results, sequences):
        """
        Parses results from a BLAST search and creates a :class:`ContigContainer`
        """
        contigs = []
        for alignment in pyblast_results.alignments:
            try:
                contigs.append(BlastContig.create_from_blast_results(alignment))
            except ContigError:
                # TODO: Should something be done here when there a ContigError?
                pass
        cc = cls(contigs=contigs, sequences=sequences)
        cc.sequences = sequences
        return cc

    def __len__(self):
        return len(self.contigs)

    def __setitem__(self, key, value):
        raise NotImplementedError("Cannot set contig")

    def __delitem__(self, key):
        del self.__contig_dictionary[key]

    def __iter__(self):
        return iter(self.__contig_dictionary)

    def __str__(self):
        return str(self.__contig_dictionary)

    def __repr__(self):
        return "ContigContainer({})".format(str(self))

    def __getitem__(self, contig_id):
        return self.__contig_dictionary[contig_id]

    def add_contig(self, contig):
        """
        Adds a contig to the ContigContainer.

        :param contig: The contig to add to the ContigContainer
        :type contig: Contig
        :return: None
        :rtype: None
        """
        if contig.contig_id not in self.__contig_dictionary:
            self.contigs.append(contig)
            self.__contig_dictionary[contig.contig_id] = contig
        else:
            raise ContigContainerError("Contig {0} alread exists in container.".format(contig))

    def add_contigs(self, contigs):
        """
        Appends a list of contigs to the ContigContainer

        :param contigs: list of type Contig
        :type contigs: list
        :return: None
        :rtype: None
        """
        for c in contigs:
            self.add_contig(c)

    # TODO: better documentation for this
    def fuse_circular_fragments(self):
        """
        'Fuses' contigs that were split only because of their origin.

        :return:
        :rtype:
        """

        def fuse_condition(l, r):
            return l.same_context(r) and \
                   l.subject.consecutive_with(r.subject) and \
                   l.query.consecutive_with(r.query) and \
                   l in self.contigs and \
                   r in self.contigs

        pairs = itertools.permutations(self.contigs, 2)
        for l, r in pairs:
            if fuse_condition(l, r):
                l.fuse(r)
                self.contigs.remove(r)

    def circular_partition(self, length):
        """This ensures that plasmids can circularize"""
        if not isinstance(length, int):
            raise TypeError("Length must be an Int")
        new_ends = []
        new_starts = []
        for c in self.contigs:
            ne = c.query.start + length
            ns = c.query.end - length
            if c.query.context.within_bounds(ne) and ne not in new_ends:
                new_ends.append(ne)
            if c.query.context.within_bounds(ns) and ns not in new_ends:
                new_ends.append(ns)

        new_contigs = []
        for c in self.contigs:
            for ne in new_ends:
                if c.query.within_region(ne):
                    c1 = c.copy()
                    c2 = c.copy()
                    c1.contig_type = "circular_partition"
                    c2.contig_type = "circular_partition"
                    c1.modify_query(c.query.start, ne)

                    c2.modify_query(ne, c.query.end)

                    new_contigs.append(c1)
                    new_contigs.append(c2)
            for ns in new_starts:
                if c.query.within_region(ns):
                    c1 = c.copy()
                    c2 = c.copy()
                    c1.contig_type = "circular_partition"
                    c2.contig_type = "circular_partition"
                    c1.modify_query(ns, c.query.end)

                    c2.modify_query(c.query.start, ns)


                    new_contigs.append(c1)
                    new_contigs.append(c2)

        self.add_contigs(new_contigs)
        return new_contigs

    def remove_redundant_contigs(self):
        """
        Removes contigs with the same start and end.

        :return: None
        :rtype: None
        """
        # pair start and end to a unique number
        # assign to dictionary
        pair_dict = {}
        for c in self.contigs:
            i = pair(c.query.start, c.query.end)
            if i not in pair_dict:
                pair_dict[i] = []
            pair_dict[i].append(c.contig_id)

        # remove redundant pairings
        for key, contigs in pair_dict.items():
            if len(contigs) > 1:
                for c in contigs[1:]:
                    del self[c]





                # def dump(self):
                #     pass
                #
                # def sort_contigs(self):
                #     """
                #     Sorts contigs according to their query start
                #     :return:
                #     """
                #     self.contigs = sorted(self.contigs, key=lambda x: x.query.start)
                #
                # def filter_perfect_subjects(self):
                #     """
                #     Selects only contigs with perfect subjects, or with
                #     subjects that have 100% of their identity contained
                #     in the contig (no partial subjects)
                #     :return: None
                #     """
                #     filtered_contigs = []
                #     for contig in self.contigs:
                #         if contig.is_perfect_subject():
                #             filtered_contigs.append(contig)
                #     self.contigs = filtered_contigs
                #
                # def remove_redundant_contigs(self):
                #     pass
                #
                #
                # def filter_by_size(self, size):
                #     filtered_contigs = []
                #     for contig in self.contigs:
                #         if contig.alignment_length > size:
                #             filtered_contigs.append(contig)
                #     self.contigs = filtered_contigs
                #
                # def filter_perfect(self):
                #     """
                #     Selects only contigs that have perfect alignment scores and are perfect subjects
                #     i.e. no gaps, no mismatches, 100% of subjects
                #     :return:
                #     """
                #     filtered_contigs = []
                #     for contig in self.contigs:
                #         if contig.is_perfect_alignment():
                #             filtered_contigs.append(contig)
                #         else:
                #             pass
                #     self.contigs = filtered_contigs
                #     # TODO: handle ambiquoous NNNN dna in blast search by eliminating gap_opens, gaps if they are N's
                #
                # def expand_contigs(self, primers):
                #     pass
                #
                # def break_contigs_at_endpoints(self):
                #     pass
