from dasi.models import Contig, ContigContainer, ContigRegion
import re

def test_find_perfect_matches():

    def perfect_matches(self, rc=True):
        """
        Pseudo-blast for finding perfect sequence matches (i.e. primers)
        :param rc:
        :return:
        """
        # Get primer sequences (defined in db)
        out, seqs, metadata = self.concate_db_to_fsa()

        contig_container = ContigContainer()

        # Get the query sequence
        query_seq = open_sequence(self.query)[0].seq
        query_seq_str = str(query_seq)
        query_seq_str = re.sub('[nN]', '.', query_seq_str).lower()

        fwd_matches = []
        rev_matches = []
        for seq in seqs:
            seq_str = str(seq.seq)
            try:
                rc_seq_str = dna_reverse_complement(seq_str)
            except KeyError:
                continue
            seq_str = re.sub('[nN]', '.', seq_str).lower()
            rc_seq_str = re.sub('[nN]', '.', rc_seq_str).lower()

            for match in re.finditer(seq_str, query_seq_str):
                subject = ContigRegion(
                    seq.id,
                    ContigRegion.START_INDEX,
                    len(seq),
                    len(seq),
                    False,
                    True,
                    sequence=seq_str,
                )

                query = ContigRegion(
                    self.query,
                    match.start() + ContigRegion.START_INDEX,
                    match.end() + ContigRegion.START_INDEX - 1,
                    self.query_length,
                    self.query_circular,
                    True,
                )

                c = Contig(query, subject, Contig.TYPE_PRIMER)
                contig_container.contigs.append(c)
            for match in re.finditer(rc_seq_str, query_seq_str):
                subject = ContigRegion(
                    seq.id,
                    len(seq),
                    ContigRegion.START_INDEX,
                    len(seq),
                    False,
                    False,
                    sequence=seq_str,
                )

                query = ContigRegion(
                    self.query,
                    match.start() + ContigRegion.START_INDEX,
                    match.end() + ContigRegion.START_INDEX - 1,
                    self.query_length,
                    self.query_circular,
                    True,
                )

                c = Contig(query, subject, Contig.TYPE_PRIMER)
                contig_container.contigs.append(c)
        return contig_container