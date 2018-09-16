"""Formatter for making GraphQL queries"""
from functools import partial


def _variable_formatter(variables):
    """
    Returns formatted types, args, and variables for formatting a GraphQL mutation or query
    :param variables: query or mutation variables of the form {argument: (type, value), ...}
    :type variables: dict
    :return: types, args, and variables dictionaries for formatting
    :rtype: tuple
    """
    if variables is None:
        return "", ""
    type_tokens = []
    arg_tokens = []
    variable_values = {}
    for k, v in variables.items():
        field_name = k
        type_name = v[0]
        variable_name = "var_{}".format(k)
        value = v[1]
        variable_values[variable_name] = value
        type_tokens.append("${}: {}".format(variable_name, type_name))
        arg_tokens.append("{}: ${}".format(field_name, variable_name))
    types = "({})".format(', '.join(type_tokens))
    args = "({})".format(', '.join(arg_tokens))

    return types, args, variable_values


def _formatter(query_name, variables, fields, t="query", name=None):
    """
    Formats a query or mutation string for GraphQL

    :param query_name: which GraphQL method to use
    :type query_name: basestring
    :param variables: query or mutation variables of the form {argument: (type, value), ...}
    :type variables: dictionary
    :param fields: output fields (e.g. \"sequence { id }\" )
    :type fields: basestring
    :param t: either "query" or "mutation"
    :type t: basestring
    :param name: optional name
    :type name: basestring
    :return: formatted GraphQL query or mutation
    :rtype: basestring
    """
    if name is None:
        name = query_name
    types, args, values = _variable_formatter(variables)
    l = "{"
    r = "}"

    str = f"""
{t} {name}{types} {l}
    {query_name}{args} {l}
        {fields.strip()}
    {r}
{r}"""

    return str.strip(), values


fmt_query = partial(_formatter, t="query")
fmt_mutation = partial(_formatter, t="mutation")


def graphql_execute(client, query_name, variables, fields, t, name=None, **kwargs):
    """
    Executes a query or mutation against a GraphQL client

    :param query_name: which GraphQL method to use
    :type query_name: basestring
    :param variables: query or mutation variables of the form {argument: (type, value), ...}
    :type variables: dictionary
    :param fields: output fields (e.g. \"sequence { id }\" )
    :type fields: basestring
    :param t: either "query" or "mutation"
    :type t: basestring
    :param name: optional name
    :type name: basestring
    :return: output data (from results['data'][query_name]) and errors
    :rtype: tuple
    """
    s, v = _formatter(query_name, variables, fields, t=t, name=name)
    result = partial(client.execute, s, variable_values=v)(**kwargs)
    errors = None
    data = None
    if 'errors' in result:
        errors = result['errors']
    if 'data' in result:
        data = result['data'][query_name]
    return data, errors


def graphql_query(client, query_name, variables, fields, name=None):
    """
    Executes a query against a GraphQL client

    :param query_name: which GraphQL method to use
    :type query_name: basestring
    :param variables: query or mutation variables of the form {argument: (type, value), ...}
    :type variables: dictionary
    :param fields: output fields (e.g. \"sequence { id }\" )
    :type fields: basestring
    :param name: optional name
    :type name: basestring
    :return: output data (from results['data'][query_name]) and errors
    :rtype: tuple
    """
    return graphql_execute(client, query_name, variables, fields, t="query", name=name)


def graphql_mutation(client, query_name, variables, fields, name=None):
    """
    Executes a mutation against a GraphQL client

    .. code:: python

        seq_variables = {"sequence": ("SequenceInput!", sequence_data)}
        seq_data, seq_errors = graphql_mutation(graphql_client, "createSequence", seq_variables, "sequence { id }")

    :param query_name: which GraphQL method to use
    :type query_name: basestring
    :param variables: query or mutation variables of the form {argument: (type, value), ...}
    :type variables: dictionary
    :param fields: output fields (e.g. \"sequence { id }\" )
    :type fields: basestring
    :param name: optional name
    :type name: basestring
    :return: output data (from results['data'][query_name]) and errors
    :rtype: tuple
    """
    return graphql_execute(client, query_name, variables, fields, t="mutation", name=name)
