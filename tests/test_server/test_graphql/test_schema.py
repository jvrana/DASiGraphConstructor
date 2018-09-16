from dasi.graphql_schema.query_formatter import graphql_mutation

def test_allSequences(graphql_client):
    executed = graphql_client.execute('''
{
    allSequences {
        edges {
            node {
                id
                bases
            }
        }
    }
}    
''')
    assert executed == {'data': {
        "allSequences": {
            "edges": []
        }
    }
    }
    print(executed)


def test_createSequence(app, graphql_client):
    """Expect creation of a sequence with expected parameters"""
    mutation = '''
    mutation createSequence($sequence: SequenceInput!) {
        createSequence(sequence: $sequence) {
            ok
            sequence {
                name
                bases
            }
        }
    }
    '''
    with app.app_context():
        seq = {
            "sequence": {
                "name": "myseq",
                "circular": False,
                "bases": "aggagataagagatat",
                "features": []
            }
        }
        executed = graphql_client.execute(mutation, variable_values=seq)
        print(dict(executed))
        ok = executed['data']["createSequence"]['ok']
        seq = executed['data']["createSequence"]['sequence']

        assert ok
        assert seq == {
            "name": "myseq",
            "bases": "aggagataagagatat"
        }


def test_createPrimer_using_formatter(app, graphql_client):

    primer_data = {
        "name": "my_primer",
        "bases": "gcgtatctgtatatcgtctgatgctgg"
    }

    with app.app_context():

        primer_variables = {"primer": ("PrimerInput!", primer_data)}
        primer_data, primer_error = graphql_mutation(graphql_client, "createPrimer", primer_variables, "ok\nprimer { name\nbases }")
        assert primer_data == {
            'ok': True,
            'primer': {
                "bases": "gcgtatctgtatatcgtctgatgctgg",
                "name": "my_primer"
            }
        }


def test_createSequence_withFeature(app, graphql_client):
    """A fairly complex test with (i) heirarchical inputs for sequence and features and
    (ii) creating sequences. We expect the creation of the sequence and feature to be
    successful and return hte sequence and feature information that was sent in."""

    mutation = '''
    mutation createSequence($sequence: SequenceInput!) {
        createSequence(sequence: $sequence) {
            ok
            sequence {
                name
                bases
                features {
                    edges {
                        node {
                            name
                            start
                            end
                            type
                            strand
                        }
                    }
                }
            }
        }
    }
    '''
    feature_variables = {
        "name": "myfeature",
        "type": "misc",
        "start": 0,
        "end": 10,
        "strand": 1
    }

    sequence_variables = {
        "sequence": {
            "name": "myseq",
            "bases": "AGTTAGA",
            "circular": False,
            "features": [feature_variables]
        }
    }

    with app.app_context():
        executed = graphql_client.execute(mutation, variable_values=sequence_variables)
        print(dict(executed))
        ok = executed['data']["createSequence"]['ok']
        seq = executed['data']["createSequence"]['sequence']

        assert ok
        assert seq == {
            "name": "myseq",
            "bases": "AGTTAGA",
            "features": {
                "edges": [
                    {"node": {
                        "name": "myfeature",
                        "start": 0,
                        "end": 10,
                        "type": "misc",
                        "strand": 1
                    }}
                ]
            }
        }


def test_run_with_pyblast(app, graphql_client):
    query = """{ alignments(queryName: "myseq") }"""

    mutation = '''
    mutation NewSequence($sequence: SequenceInput!) {
        createSequence(sequence: $sequence)
           ok
            sequence {
                name
                bases
            }
        }
    }
    '''

    sequence_data = {
        "sequence": {
            "name": "myseq",
            "bases": "aaacttcccaccccataccctattaccactgccaattacctagtggtttcatttactctaaacctgtgattcctctgaattattttcatttta",
            "circular": False,
        }
    }

    with app.app_context():
        graphql_client.execute(mutation, variable_values=sequence_data)
        executed = graphql_client.execute(query)
        print(executed)
        # assert executed['data']['alignments'] is not None


def test_createResults(app, graphql_client):
    create_sequence = '''
    mutation newSequence($sequence: SequenceInput!) {
        createSequence(sequence: $sequence) {
           ok
           sequence {
                id
                name
                bases
            }
        }
    }
    '''

    create_alignment = '''
        mutation createAlignment($query_id: ID!, $subject_ids: [ID]) {
            createAlignment(subjectIds: $subject_ids, queryId: $query_id) {
                ok
                results {
                    id
                    queryId
                    subjectId
                    alignmentScoreId
                    query {
                        bases
                    }
                    subject {
                        bases
                    }
                    alignmentScore {
                        id
                    }
                }
            }
        }
    '''

    with app.app_context():
        sequence_data = {
            "sequence": {
                "name": "myseq",
                "bases": "atgctgacgcgcgtatctgtatatcgtctgatgctggcgcgattttgctagcagtctatattcgtagctgac",
                "circular": False,
                "features": []
            }
        }
        executed = graphql_client.execute(create_sequence, variable_values=sequence_data)
        print(executed)
        executed = graphql_client.execute(create_sequence, variable_values=sequence_data)
        nodes = graphql_client.execute('''{allSequences {edges {node {id}}}}''')['data']['allSequences']['edges']
        seq_ids = [x['node']['id'] for x in nodes]
        query_id = executed['data']['createSequence']['sequence']['id']
        executed = graphql_client.execute(create_alignment,
                                          variable_values={"query_id": query_id, "subject_ids": None})
        print(executed)
        if 'errors' in executed:
            msg = ""
            for i, e in enumerate(executed['errors']):
                msg += "  ({}) {} {} {}\n".format(i, e['message'], e['locations'], e['path'])
            raise Exception("There were errors that occured during GraphQL execution.\n{}".format(msg))
        results = executed['data']['createAlignment']['results']
        print(results)


def test_createPrimerResults(app, graphql_client):

    with app.app_context():
        # load sequence
        sequence_data = {
            "name": "myseq",
                "bases": "atgctgacgcgcgtatctgtatatcgtctgatgctggcgcgattttgctagcagtctatattcgtagctgac",
                "circular": False,
                "features": []
        }
        seq_variables = {"sequence": ("SequenceInput!", sequence_data)}
        seq_data, seq_errors = graphql_mutation(graphql_client, "createSequence", seq_variables, "sequence { id }")
        assert seq_data is not None
        assert seq_errors is None

        # load primer
        primer_data = {
            "name": "my_primer",
            "bases": "gcgtatctgtatatcgtctgatgctgg"
        }
        primer_variables = {"primer": ("PrimerInput!", primer_data)}
        primer_data, primer_errors = graphql_mutation(graphql_client, "createPrimer", primer_variables, "primer { id }")
        assert primer_data is not None
        assert primer_errors is None

        # get results
        variables = {"queryId": ("ID!", seq_data['sequence']['id'])}
        results_data, results_error = graphql_mutation(graphql_client, "createPrimerResults", variables, "results { id }")
        assert results_data is not None
        assert results_error is None

        assert len(results_data['results']) == 2


def test_sequences(app, graphql_client):

    with app.app_context():
        e = graphql_client.execute("{ sequences { id } }")
        print(e)


def test_createResults_with_rc_sequence(app, graphql_client):

    with app.app_context():

        seq1 = {
            "name": "myseq",
            "circular": False,
            "bases": "aaaactgtattataagtaaatgcatgtatactaaactcacaaattagagcttcaatttaattatatcagttattacccgggaatctcggtcgtaat" \
                        "gatttctataatgacgaaaaaaaaaaaattggaaagaaaaagcttcatggcctttataaaaaggaactatccaatacctcgccagaaccaagtaacagtatttt" \
                        "acggggcacaaatcaagaacaataaga",
            "features": []
        }

        seq2 = {
            "name": "myseq",
            "circular": False,
            "bases": "ttccaattttttttttttcgtcattatagaaatcattacgaccgagattccc",
            "features": []
        }

        seq1_res, errors = graphql_mutation(graphql_client, "createSequence", {"sequence": ("SequenceInput!", seq1)}, "ok\nsequence { id }")
        seq2_res, errors = graphql_mutation(graphql_client, "createSequence", {"sequence": ("SequenceInput!", seq2)}, "ok\nsequence { id }")

        query_id = seq1_res['sequence']['id']

        fields = """
        results {
            id
            query {
                bases
                start
                end
                strand
            }
            subject {
                bases
                start
                end
                strand
            }
        }"""
        results, errors = graphql_mutation(graphql_client, "createResults", {"queryId": ("ID!", query_id)}, fields)
        print(errors)
        print(results)