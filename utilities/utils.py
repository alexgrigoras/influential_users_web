import dash_table


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
