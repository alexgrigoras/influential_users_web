import pickle

import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

from application.message_logger import MessageLogger
from application.plotly_display import visualize_graph_3d, visualize_graph
from utilities.utils import check_value

NETWORKS_FOLDER = '.networks'
IMAGES_FOLDER = '.images'
TEXT_EXTENSION = '.txt'
OBJECT_EXTENSION = '.pickle'
NETWORK_OBJECT_EXTENSION = '.gpickle'
GRAPH_EXTENSION = '.gexf'
IMAGE_EXTENSION = '.png'
DOT_EXTENSION = '.dot'


class NetworkAnalysis:
    """

    """

    def __init__(self, file_name=None):
        """
        Class constructor
        """
        # logging module
        ml = MessageLogger('network_analysis')
        self.logger = ml.get_logger()

        # variables
        self.__graph = nx.empty_graph
        self.__labels = {}
        self.__rank = []
        self.__file_name = file_name

    def set_file_name(self, file_name):
        """
        Sets the name of the file to read for input and also for exporting data to a specific format
        :param file_name: name of the file without extension
        """
        self.__file_name = file_name

    def get_graph_info(self):
        """
        Prints the graph information
        :return: returns the graph information
        """
        return nx.info(self.__graph)

    def export_to_gexf(self):
        """
        Export network to gexf format. A file name needs to be set before performing this operation
        """
        if not self.__file_name:
            self.logger.critical("No file name was set")
            exit(0)

        nx.write_gexf(self.__graph, NETWORKS_FOLDER + "/" + self.__file_name + GRAPH_EXTENSION)

    def export_to_dot(self):
        """
        Export network to gexf format. A file name needs to be set before performing this operation
        """
        if not self.__file_name:
            self.logger.critical("No file name was set")
            exit(0)

        # write dot file to use with graphviz - run "dot -Tpng file_name.svg > file_name.svg"
        nx.nx_agraph.write_dot(self.__graph, NETWORKS_FOLDER + "/" + self.__file_name + DOT_EXTENSION)

    def create_network(self):
        """
        Creates a network from the file with the edge-list.
        A file name needs to be set before performing this operation
        """
        if not self.__file_name:
            self.logger.critical("No file name was set")
            exit(0)

        self.__graph = nx.read_edgelist(NETWORKS_FOLDER + "/" + self.__file_name + TEXT_EXTENSION,
                                        create_using=nx.Graph(),
                                        edgetype=str, delimiter=" ")

        self.__labels = pickle.load(open(NETWORKS_FOLDER + "/" + self.__file_name + OBJECT_EXTENSION, "rb"))

    def store_network(self):
        self.logger.info("Stored network: " + NETWORKS_FOLDER + "/" + self.__file_name + NETWORK_OBJECT_EXTENSION)
        nx.write_gpickle(self.__graph, NETWORKS_FOLDER + "/" + self.__file_name + NETWORK_OBJECT_EXTENSION)
        self.store_ranks()

    def store_ranks(self):
        pickle.dump(self.__rank, open(NETWORKS_FOLDER + "/ranks-" + self.__file_name + OBJECT_EXTENSION, "wb"))

    def store_labels(self):
        pickle.dump(self.__labels, open(NETWORKS_FOLDER + "/" + self.__file_name + OBJECT_EXTENSION, "wb"))

    def import_network(self):
        self.logger.info("Imported network " + NETWORKS_FOLDER + "/" + self.__file_name + NETWORK_OBJECT_EXTENSION)
        self.__graph = nx.read_gpickle(NETWORKS_FOLDER + "/" + self.__file_name + NETWORK_OBJECT_EXTENSION)
        self.__labels = pickle.load(open(NETWORKS_FOLDER + "/" + self.__file_name + OBJECT_EXTENSION, "rb"))
        self.__rank = pickle.load(open(NETWORKS_FOLDER + "/ranks-" + self.__file_name + OBJECT_EXTENSION, "rb"))

    def compute_page_rank(self):
        """
        Calculates the values of the nodes using page rank algorithm and prints them
        """
        self.__rank = nx.pagerank(self.__graph, alpha=0.9)

    def compute_vote_rank(self):
        """
        Calculates the values of the nodes using vote rank algorithm and prints them
        """
        self.__rank = self.vote_rank(self.__graph)

    def compute_betweenness_centrality(self):
        """
        Calculates the values of the nodes using  algorithm and prints them
        """
        self.__rank = nx.betweenness_centrality(self.__graph, normalized=True, endpoints=True)

    def get_ranks(self):
        return self.__rank

    def display_rank(self, algorithm_name):
        """
        Prints the first 5 nodes with the highest values
        :param algorithm_name: tha name of the algorithm used
        """
        values = sorted(self.__rank, key=self.__rank.get, reverse=True)[:5]
        print(algorithm_name + ":")
        for i, v in enumerate(values, start=1):
            print("\t" + str(i) + ". " + self.__labels[v])

    def __configure_display(self, title):
        plt.title(title)
        plt.figure(figsize=(30, 30))
        plt.axis('off')
        node_color = []
        node_size = []

        if self.__rank:
            node_color = [20000.0 * self.__graph.degree(v) for v in self.__graph]
            node_size = [v * 10000 for v in self.__rank.values()]

        return node_color, node_size

    def __draw(self):
        """
        Display the graph and
        """
        plt.savefig(IMAGES_FOLDER + "/" + self.__file_name + IMAGE_EXTENSION)
        plt.show()

    def display_tree(self):
        """
        Display the created tree
        """
        node_color, node_size = self.__configure_display('Tree')
        pos = graphviz_layout(self.__graph, prog='dot')
        tree = nx.minimum_spanning_tree(self.__graph)

        nx.draw_networkx(tree, pos=pos, with_labels=False, node_color=node_color, node_size=node_size,
                         labels=self.__labels)
        self.__draw()

    @staticmethod
    def __check_value(array, value):
        if value in array:
            return array[value]
        else:
            return "x"

    def display_plotly(self, nodes, graph_type):
        subgraph = self.__graph.subgraph(nodes)
        node_sizes = self.get_node_sizes(subgraph)
        # edge_weights = self.get_edge_weights(graph)
        node_ids = self.get_node_labels(subgraph)
        node_labels = [self.__check_value(self.__labels, n_id) for n_id in node_ids]
        edge_weights = None

        if graph_type == "3":
            fig = visualize_graph_3d(subgraph, node_labels, node_sizes, "spring", "3D visualization")
        elif graph_type == "2":
            tree = nx.minimum_spanning_tree(subgraph)
            fig = visualize_graph(tree, node_labels, node_sizes, edge_weights, "graphviz", "2D visualization")
        else:
            return None

        return fig

    def create_figure(self, limit, graph_type):
        columns = ['Rank', 'Value', 'Name']
        values = []
        index = 0
        selected_nodes = []

        for u_id in sorted(self.__rank, key=self.__rank.get, reverse=True):
            selected_nodes.append(u_id)
            val = {"Rank": index + 1, "Value": check_value(self.__rank, u_id), 'Name': check_value(self.__labels, u_id)}
            values.append(val)
            index += 1
            if index >= limit:
                break

        fig = self.display_plotly(selected_nodes, graph_type)

        return fig, values, columns

    def get_labels(self):
        return self.__labels

    def get_nr_nodes(self):
        return len(self.__graph)

    @staticmethod
    def get_edge_weights(graph):
        weights = [graph[u][v]['weight'] for u, v in graph.edges()]
        return weights

    @staticmethod
    def get_node_sizes(graph):
        node_sizes = nx.get_node_attributes(graph, 'importance').values()
        return node_sizes

    @staticmethod
    def get_node_labels(graph):
        return graph.nodes()

    @staticmethod
    def vote_rank(graph, number_of_nodes=None):
        """
        Updated function from networkx to return the number of votes for each node

        Select a list of influential nodes in a graph using VoteRank algorithm

        VoteRank [1]_ computes a ranking of the nodes in a graph G based on a
        voting scheme. With VoteRank, all nodes vote for each of its in-neighbours
        and the node with the highest votes is elected iteratively. The voting
        ability of out-neighbors of elected nodes is decreased in subsequent turns.

        Note: We treat each edge independently in case of multigraphs.

        Parameters
        ----------
        graph : graph
            A NetworkX graph.

        number_of_nodes : integer, optional
            Number of ranked nodes to extract (default all nodes).

        Returns
        -------
        voterank : list
            Ordered list of computed seeds.
            Only nodes with positive number of votes are returned.

        References
        ----------
        .. [1] Zhang, J.-X. et al. (2016).
            Identifying a set of influential spreaders in complex networks.
            Sci. Rep. 6, 27823; doi: 10.1038/srep27823.
        """
        influential_nodes = []
        results = {}
        voterank = {}

        if len(graph) == 0:
            return influential_nodes
        if number_of_nodes is None or number_of_nodes > len(graph):
            number_of_nodes = len(graph)
        if graph.is_directed():
            # For directed graphs compute average out-degree
            avgDegree = sum(deg for _, deg in graph.out_degree()) / len(graph)
        else:
            # For undirected graphs compute average degree
            avgDegree = sum(deg for _, deg in graph.degree()) / len(graph)
        # step 1 - initiate all nodes to (0,1) (score, voting ability)
        for n in graph.nodes():
            voterank[n] = [0, 1]
            results[n] = voterank[n][0]
        # Repeat steps 1b to 4 until num_seeds are elected.
        for _ in range(number_of_nodes):
            # step 1b - reset rank
            for n in graph.nodes():
                voterank[n][0] = 0
            # step 2 - vote
            for n, nbr in graph.edges():
                # In directed graphs nodes only vote for their in-neighbors
                voterank[n][0] += voterank[nbr][1]
                if not graph.is_directed():
                    voterank[nbr][0] += voterank[n][1]
            for n in influential_nodes:
                voterank[n][0] = 0
            # step 3 - select top node
            n = max(graph.nodes, key=lambda x: voterank[x][0])
            if voterank[n][0] == 0:
                return results

            influential_nodes.append(n)
            results[n] = voterank[n][0]

            # weaken the selected node
            voterank[n] = [0, 0]
            # step 4 - update voterank properties
            for _, nbr in graph.edges(n):
                voterank[nbr][1] -= 1 / avgDegree
                voterank[nbr][1] = max(voterank[nbr][1], 0)

        return results
