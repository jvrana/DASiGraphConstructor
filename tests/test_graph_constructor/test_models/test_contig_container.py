from core.graph_constructor.models import ContigContainer


def test_contig_container_parse_from_results(aligner):
    new_cc = ContigContainer.parse_alignments(aligner.results.alignments)
    assert len(new_cc.contigs) > 0

def test_contig_container_fixture(cc):
    assert len(cc.contigs) > 0

def test_fuse(cc):
    cc.fuse_circular_fragments()


