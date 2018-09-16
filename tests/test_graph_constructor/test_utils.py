import os
from dasi.graph_constructor.utils import pseudocircularize
from Bio import SeqIO


def test_pseudocircular(seq_dir, tmpdir):
    inpath = os.path.join(seq_dir, 'reindexed_design/test.gb')

    # open sequence
    seq = None
    with open(inpath, 'r') as f:
        seq = SeqIO.read(f, "genbank")

    # pseudocircularize it
    outpath = os.path.join(tmpdir, 'test_pseudocircularized.gb')
    pseudocircularize(inpath, outpath)

    # check
    with open(outpath, 'r') as f:
        new_seq = SeqIO.read(f, "genbank")
        assert len(new_seq) == 2 * len(seq)
        assert str(new_seq.seq) == str(seq.seq) * 2