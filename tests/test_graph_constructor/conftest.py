import os
import json

import pytest
from core.graph_constructor.models import ContigContainer
from pyblast import JSONBlast


TEST_DIR = os.path.dirname(os.path.realpath(__file__))
BLAST_DIR = os.path.join(TEST_DIR, 'data/blast')
SEQ_DIR = os.path.join(TEST_DIR, 'data/test_sequences')


@pytest.fixture(scope="module")
def test_dir():
    return TEST_DIR


@pytest.fixture(scope='module')
def seq_dir():
    return SEQ_DIR



@pytest.fixture(scope="function")
def aligner():
    subject_path = os.path.join(TEST_DIR,
                                "data/test_sequences/templates.json")
    query_path = os.path.join(TEST_DIR,
                              "data/test_sequences/query.json")

    with open(subject_path, 'r') as f:
        subject = json.load(f)


    with open(query_path, 'r') as f:
        query = json.load(f)

    jsonblast = JSONBlast(
        subject,
        query,
        span_origin=True,
    )
    jsonblast.quick_blastn()
    return jsonblast

@pytest.fixture(scope="function")
def cc():
    a = aligner()
    cc = ContigContainer.parse_alignments(a.results, list(a.seq_dict.values()))
    return cc

# _cc = ContigContainer.parse_alignments(aligner().results, sequences=aligner().seq_db.sequences)
# _pseudocircular_cc = ContigContainer.find_alignments(aligner().input_dir,
#                                                      aligner().query_path, force_linear=False)
#
# @pytest.fixture(scope="function")
# def cc():
#     return deepcopy(_cc)
#
#
#
#
# @pytest.fixture(scope="function")
# def pseudocircular_cc():
#     return deepcopy(_pseudocircular_cc)
#


        # @pytest.fixture
    # def config(scope="module"):
    #     test_dir = os.path.dirname(os.path.abspath(__file__))
    #     config_location = os.path.join(test_dir, "secrets/config.json")
    #     with open(config_location, 'rU') as handle:
    #         return json.load(handle)
    #
    # @pytest.fixture(scope="module")
    # def api():
    #     return BenchlingAPI(**config()["credentials"])

    # @pytest.fixture
    # def query_subject_example(scope="module"):
    #     subject = ContigRegion(911, 757, 9795, "pRIAS_(CC#15)", True, False, filename="templates/pRIAS (CC15).gb")
    #
    #     query = ContigRegion(1, 155, 22240, "pRIAS_(CC#15)", True, True, filename="templates/pfsfsfRIAS (CC15).gb")
    #     return [query, subject]

    # @pytest.fixture
    # def create_contigs(scope="module"):
    #     def wrapper(list_of_start_and_ends):
    #         contigs = []
    #         for x, y in list_of_start_and_ends:
    #             c = contig_example.copy()
    #             c.query.start = x
    #             c.query.end = y
    #             contigs.append(c)
    #         return contigs
    #     return wrapper
