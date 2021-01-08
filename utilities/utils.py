import dash_table

graph_actions = {
    "Delete": "delete",
    "Change algorithm": "change-algorithm",
    "Change graph type": "change-graph"
}
graph_types = {
    "3D Spring": '3',
    "2D Graph": '2'
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
