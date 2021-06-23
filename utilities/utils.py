import os
import random
import string

import dash_table

STRING_LENGTH = 10
COMMENT_PAGES_LIMIT = 5
NR_VIDEOS_LIMIT = 50
NETWORKS_FOLDER = ".networks/"

graph_actions = {
    "Delete": "delete",
    "Change algorithm": "change-algorithm",
    "Change graph type": "change-graph",
}
graph_types = {
    "3D Spring": 'spring',
    "3D Kamada Kawai": 'kamada-kawai',
}
processing_algorithms = {
    "Betweenness centrality": "betweenness-centrality",
    "Degree centrality": "degree-centrality",
    "Closeness centrality": "closeness-centrality",
    "Eigenvector centrality": "eigenvector-centrality",
    "Load centrality": "load-centrality",
    "Harmonic centrality": "harmonic-centrality",
    "PageRank": "page-rank",
    "VoteRank": "vote-rank",
}


def create_data_table_network(values, columns):
    """
    Create Dash datatable from Pandas DataFrame.
    :param columns: the input columns
    :param values: the input values
    :return: the generated table
    """
    table = dash_table.DataTable(
        id='database-table',
        columns=[{"name": i, "id": i} for i in columns],
        data=values,
        sort_action="native",
        sort_mode='single',
        page_size=10,
        style_cell={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': 0
        }
    )
    return table


def check_value(array, value):
    """
    Checks if a value exists in an array
    :param array: the input array
    :param value: the searched value
    :return: the returned value or "x"
    """
    if value in array:
        return array[value]
    else:
        return "x"


def create_file_name():
    """
    Generates a random string
    :return: the generated string
    """
    file_name = "network_" + __random_string(STRING_LENGTH)
    while os.path.exists(NETWORKS_FOLDER + file_name + ".*"):
        file_name = "network_" + __random_string(STRING_LENGTH)

    return file_name


def __random_string(string_length):
    """
    Generate a random string with the combination of lowercase and uppercase letters
    :param string_length: the length of the string that is generated
    :return: the generated string
    """
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(string_length))