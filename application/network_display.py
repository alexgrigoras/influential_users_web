import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.readwrite.adjlist import generate_adjlist
from plotly.graph_objs import *


def reformat_graph_layout(graph, layout):
    """
    this method provide positions based on layout algorithm
    :param graph:
    :param layout:
    :return:
    """
    if layout == "graphviz":
        positions = graphviz_layout(graph)
    elif layout == "spring":
        positions = nx.fruchterman_reingold_layout(graph, dim=3, k=0.5, iterations=1000)
    elif layout == "spectral":
        positions = nx.spectral_layout(graph, scale=0.1)
    elif layout == "random":
        positions = nx.random_layout(graph)

    else:
        raise Exception("please specify the layout from graphviz, spring, spectral or random")

    return positions


def visualize_graph(graph, node_labels, node_sizes=None, edge_weights=None, layout="graphviz", title=""):
    """
    :param graph:
    :param node_labels:
    :param node_sizes:
    :param edge_weights:
    :param layout:
    :param filename:
    :param title:
    :return:
    """
    if edge_weights is None:
        edge_weights = []
    if node_sizes is None:
        node_sizes = []

    positions = reformat_graph_layout(graph, layout)

    edge_trace = Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),  # Line(width=[], color='rgba(136, 136, 136, .8)'),
        hoverinfo='none',
        mode='lines')

    for edge in graph.edges():
        x0, y0 = positions[edge[0]]
        x1, y1 = positions[edge[1]]
        edge_trace['x'] += [x0, x1, None]
        edge_trace['y'] += [y0, y1, None]

    if edge_weights:
        for weight in edge_weights:
            edge_trace['line']['width'].append(weight)
    else:
        edge_trace['line']['width'] = [1] * len(graph.edges())

    node_trace = Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        # textfont=dict(family='Calibri (Body)', size=25, color='black'),
        # opacity=100,
        hoverinfo='text',
        marker=Marker(
            showscale=True,
            # colorscale options
            # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=100,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2))
    )

    for node in graph.nodes():
        x, y = positions[node]
        node_trace['x'].append(x)
        node_trace['y'].append(y)

    for adjacencies in generate_adjlist(graph):
        node_trace['marker']['color'].append(len(adjacencies))

    if not node_labels:
        node_labels = graph.nodes()

    for node in node_labels:
        node_trace['text'].append(node)

    if node_sizes:
        for size in node_sizes:
            node_trace['marker']['size'].append(size)
    else:
        node_trace['marker']['size'] = [10] * len(graph.nodes())

    fig = Figure(data=Data([edge_trace, node_trace]),
                 layout=Layout(
                     title=title,
                     titlefont=dict(size=16),
                     showlegend=False,
                     height=800,
                     hovermode='closest',
                     margin=dict(b=20, l=5, r=5, t=40),
                     # family='Courier New, monospace', size=18, color='#7f7f7f',
                     annotations=[dict(
                         text="",
                         showarrow=False,
                         xref="paper", yref="paper",
                         x=0.005, y=-0.002)],
                     xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False),
                     yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))

    return fig


def visualize_graph_3d(graph, node_labels, node_sizes, layout="spring", title="3D Visualization"):
    """

    :param layout:
    :param graph:
    :param node_labels:
    :param node_sizes:
    :param title:
    :return:
    """
    edge_trace = Scatter3d(x=[],
                           y=[],
                           z=[],
                           mode='lines',
                           line=Line(color='rgba(136, 136, 136, .8)', width=1),
                           hoverinfo='none'
                           )

    node_trace = Scatter3d(x=[],
                           y=[],
                           z=[],
                           mode='markers',
                           # name='actors',
                           marker=Marker(symbol='dot',
                                         size=[],
                                         color=[],
                                         colorscale='Jet',  # 'Viridis',
                                         line=Line(color='rgb(50,50,50)', width=0.5)
                                         ),
                           text=[],
                           hoverinfo='text'
                           )

    positions = reformat_graph_layout(graph, layout)

    for edge in graph.edges():
        x0, y0, z0 = positions[edge[0]]
        x1, y1, z1 = positions[edge[1]]
        edge_trace['x'] += [x0, x1, None]
        edge_trace['y'] += [y0, y1, None]
        edge_trace['z'] += [z0, z1, None]

    for node in graph.nodes():
        x, y, z = positions[node]
        node_trace['x'].append(x)
        node_trace['y'].append(y)
        node_trace['z'].append(z)

    for adjacencies in generate_adjlist(graph):
        node_trace['marker']['color'].append(len(adjacencies))

    for size in node_sizes:
        node_trace['marker']['size'].append(size)

    for node in node_labels:
        node_trace['text'].append(node)

    axis = dict(showbackground=False,
                showline=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                title=''
                )

    layout = Layout(
        title=title,
        height=1000,
        margin=Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=0  # top margin
        ),
        showlegend=False,
        scene=Scene(
            xaxis=XAxis(axis),
            yaxis=YAxis(axis),
            zaxis=ZAxis(axis),
        ),
        hovermode='closest',
        annotations=Annotations([
            Annotation(
                showarrow=False,
                text="",
                xref='paper',
                yref='paper',
                x=0,
                y=0.1,
                xanchor='left',
                yanchor='bottom',
                font=Font(
                    size=14
                )
            )
        ]), )

    data = Data([node_trace, edge_trace])
    fig = Figure(data=data, layout=layout)

    return fig
