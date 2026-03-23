'''
Main to perform geocoding, choosing between "only Nominatim" and "Nominatim + NER"
'''

import argparse
import os
import json
from network_creation import *


parser = argparse.ArgumentParser(description='Network creation from edgelist')
parser.add_argument('-df_to_edgelist',
                    type=str,
                    default='todo',
                    help='If we need to translate an edgelist in df format into list format -> todo')
parser.add_argument('-df_edgelist',
                    type=str,
                    help='DF edgelist path')
parser.add_argument('-source_col',
                    type=str,
                    default='source',
                    help='Name of source column')
parser.add_argument('-target_col',
                    type=str,
                    default='target',
                    help='Name of target column')
parser.add_argument('-edge_properties_cols',
                    type=list,
                    default=['link'],
                    help='List of edge properties names in the df')
parser.add_argument('-df_to_nodes_attr',
                    type=str,
                    default='todo',
                    help='If we need to translate an nodes attributes in df format into dictionary format -> todo')
parser.add_argument('-df_nodes_attr',
                    type=str,
                    help='DF nodes path')
parser.add_argument('-node_attr_cols',
                    type=list,
                    default=[],
                    help='List of nodes properties names in the df')
parser.add_argument('-network_type',
                    type=str,
                    default='directed',
                    help='Network types: directed, undirected, multiedge_directed, multiedge_undirected')
parser.add_argument('-output',
                    type=str,
                    default='output.graphml',
                    help='Output file')



if __name__ == '__main__':

    '''args = parser.parse_args()

    # only nominatim -> we use function that writes on csv step by step
    if args.df_to_edgelist == 'todo':
        print('si')
        #print(args.df_edgelist)
        df_edgelist = pd.read_csv(args.df_edgelist)
        edgelist = df_edgelist_to_list_edgelist(df_edgelist, args.source_col, args.target_col, args.edge_properties_cols)
    else:
        edgelist = {}

    if args.df_to_nodes_attr == 'todo':
        df_nodes = pd.read_csv(args.df_nodes_attr)
        dict_nodes = df_nodes_to_dict_nodes(df_nodes, args.node_col, args.node_attr_cols)
    else:
        dict_nodes = {}

    create_network_nx(edgelist, dict_nodes, args.network_type, args.output)
    g = nx.read_graphml('output.graphml')
    print('Nodes')
    print(g.nodes(data=True))
    print('Edges')
    print(g.edges(data=True))'''


