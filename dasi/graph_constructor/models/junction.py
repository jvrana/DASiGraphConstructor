"""

This module contains methods for determining the 'cost' of an
assembly junction

"""

def example_determine_assembly_jxn_cost(left, right):
    """
    Determines the cost of an assembly junction

    :param left: the left contig region
    :param right: the right contig region
    :return: cost of the assembly junction
    """

    # if left is extendable, that means this 'fragment' is created by using a primer
    # else, this fragment has already been generated and cannot be extended
    left.end_extendable

    # if right is extendable, that means this 'fragment' is created by using a primer
    # else, this fragment has already been generated and cannot be extended
    right.start_extendable

    # do something with the distance between the regions and whether regions are
    # extendable or not.


    """
    left        |----------|
    right                      |-----------|
    span
    """
    return left.get_gap_span(right)



