import os
import random
import string

import dash_table

STRING_LENGTH = 10
COMMENT_PAGES_LIMIT = 3
NETWORKS_FOLDER = ".networks/"

graph_actions = {
    "Delete": "delete",
    "Change algorithm": "change-algorithm",
    "Change graph type": "change-graph"
}
graph_types = {
    "3D Spring": 'spring',
    "3D Graphviz": 'graphviz',
    "3D Spectral": 'spectral',
    "3D Random": 'random',
    "2D Graph": '2d',
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
    "GNN Ranking": "gnn-ranking",
}


def create_data_table_network(values, columns):
    """
    Create Dash datatable from Pandas DataFrame.
    :param columns:
    :param labels:
    :param values:
    :return:
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
    if value in array:
        return array[value]
    else:
        return "x"


def create_file_name():
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