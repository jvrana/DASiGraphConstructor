"""
DASi utilities
"""

import contextlib
import math
import sys

from dasi.graph_constructor.exceptions import SequenceError


# def generate_random_primers(seq, out, num_primers=5, min_size=15, max_size=60):
#     rand_pos = np.random.randint(0, len(seq) - max_size, size=num_primers)
#     rand_size = np.random.randint(min_size, max_size, size=num_primers)
#     primers = []
#     for pos, size in zip(rand_pos, rand_size):
#         primer = seq[pos:pos + size]
#         primer.id = primer.id + '{}-{}'.format(pos, pos + size)
#
#         rc = np.random.choice(['rc', ''])
#         if rc == 'rc':
#             primer = primer.reverse_complement(id=primer.id + '_rc')
#         primers.append(primer)
#     save_sequence(out, primers)
#     return out


# def dump_coral_to_json(path, outpath, width=700):
#     seq = coral.seqio.read_dna(path)
#     print(path)
#     print(seq.features)
#     print(seq.features[0].__dict__)
#     print(list(seq.__dict__.keys()))
#
#     def to_json(c, outpath):
#         d = c.__dict__
#         d['width'] = width
#         d['height'] = d['width']
#         d['length'] = len(c)
#         d['features'] = [x.__dict__ for x in c.features]
#         del d['top']
#         del d['bottom']
#         with open(outpath, 'w') as handle:
#             json.dump(d, handle)
#
#     to_json(seq, outpath)


def pair(k1, k2, safe=True):
    """
    The Cantor pairing function. Uniquely encodes two natural numbers into a single natural number.

    http://en.wikipedia.org/wiki/Pairing_function#Cantor_pairing_function
    """
    z = int(0.5 * (k1 + k2) * (k1 + k2 + 1) + k2)
    if safe and (k1, k2) != depair(z):
        raise ValueError("{} and {} cannot be paired".format(k1, k2))
    return z


def depair(z):
    """
    Inverse of Cantor pairing function. Decodes a natural number into to natural numbers.

    http://en.wikipedia.org/wiki/Pairing_function#Inverting_the_Cantor_pairing_function
    """
    w = math.floor((math.sqrt(8 * z + 1) - 1) / 2)
    t = (w ** 2 + w) / 2
    y = int(z - t)
    x = int(w - y)
    # assert z != pair(x, y, safe=False):
    return x, y


def pseudocircularize(inpath, outpath):
    """
    Creates a pseudocircular DNA sequence from a linear sequence for use in BLAST searches.
    This will concatenate the same sequence so that searches can search can 'wrap' over the
    origin of sequences. This will save a new sequence file

    :param inpath: path to the input sequence
    :type inpath: basestring
    :param outpath: path to save output sequence
    :type outpath: basestring
    :return: pseudocircularize sequence
    :rtype: PySequence
    """
    seqs = PySequence.parse(inpath)
    if len(seqs) > 1:
        raise SequenceError(f"More than one sequence found ({len(seqs)}) at {inpath}")
    elif len(seqs) == 0:
        raise SequenceError(f"No sequences found at {inpath}")
    seq = seqs[0]
    seq.seq = seq.seq + seq.seq
    PySequence.save_sequences(outpath, [seq])
    return seq


def dna_complement(sequence):
    d1 = 'atgcn'
    d2 = 'tacgn'
    dic = dict(
        list(zip(
            list(d1.lower()) + list(d1.upper()),
            list(d2.lower()) + list(d2.upper())
        ))
    )
    rc = ''.join([dic[x] for x in sequence])
    return rc


def dna_reverse_complement(sequence):
    return dna_complement(sequence)[::-1]


class DummyFile(object):
    def write(self, x): pass

    def flush(self, *args): pass



@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    yield
    sys.stdout = save_stdout

# def perfect_matches(self, rc=True):
#     """
#     Pseudo-blast for finding perfect sequence matches (i.e. primers)
#     :param rc:
#     :return:
#     """
#     # Get primer sequences (defined in db)
#     out, seqs, metadata = self.concate_db_to_fsa()
#
#     contig_container = ContigContainer()
#
#     # Get the query sequence
#     query_seq = open_sequence(self.query)[0].seq
#     query_seq_str = str(query_seq)
#     query_seq_str = re.sub('[nN]', '.', query_seq_str).lower()
#
#     fwd_matches = []
#     rev_matches = []
#     for seq in seqs:
#         seq_str = str(seq.seq)
#         try:
#             rc_seq_str = dna_reverse_complement(seq_str)
#         except KeyError:
#             continue
#         seq_str = re.sub('[nN]', '.', seq_str).lower()
#         rc_seq_str = re.sub('[nN]', '.', rc_seq_str).lower()
#
#         for match in re.finditer(seq_str, query_seq_str):
#             subject = ContigRegion(
#                 seq.id,
#                 ContigRegion.START_INDEX,
#                 len(seq),
#                 len(seq),
#                 False,
#                 True,
#                 sequence=seq_str,
#             )
#
#             query = ContigRegion(
#                 self.query,
#                 match.start() + ContigRegion.START_INDEX,
#                 match.end() + ContigRegion.START_INDEX - 1,
#                 self.query_length,
#                 self.query_circular,
#                 True,
#             )
#
#             c = Contig(query, subject, Contig.TYPE_PRIMER)
#             contig_container.contigs.append(c)
#         for match in re.finditer(rc_seq_str, query_seq_str):
#             subject = ContigRegion(
#                 seq.id,
#                 len(seq),
#                 ContigRegion.START_INDEX,
#                 len(seq),
#                 False,
#                 False,
#                 sequence=seq_str,
#             )
#
#             query = ContigRegion(
#                 self.query,
#                 match.start() + ContigRegion.START_INDEX,
#                 match.end() + ContigRegion.START_INDEX - 1,
#                 self.query_length,
#                 self.query_circular,
#                 True,
#             )
#
#             c = Contig(query, subject, Contig.TYPE_PRIMER)
#             contig_container.contigs.append(c)
