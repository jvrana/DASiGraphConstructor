from dasi.graph_constructor.models import BlastContig

def test_blast_contig_constructor(aligner):
    alignments = aligner.results.alignments
    bc = BlastContig.create_from_blast_results(alignments[0])
    pass
