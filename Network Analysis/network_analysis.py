import pandas as pd
import numpy as np
import csv
import networkx as nx
from utilsss import *


# network degree

def network_degree(g, node_col, output):
    '''
    Given a graph in nx, it returns a df with nodes degree and it saves it in output
    g: graph nx
    node_col: name to give to the node column
    output: output file for the degree df
    '''

    degree_dict = dict(g.degree(weight='weight'))

    for node, degree in degree_dict.items():
        print(f"Node {node}: Degree (with weights) {degree}")
    
    # degree df for viualization
    node_list = degree_dict.keys()

    degree_df = pd.DataFrame(columns=[node_col, 'degree'], index=node_list)

    for node, degree in degree_dict.items():
        degree_df.at[node, 'degree'] = degree
    
    degree_df[node_col] = node_list

    # sort by degree
    degree_df = degree_df.sort_values(by='degree', ascending=False)

    # save degree df
    degree_df.to_csv(output, index=False)

    return degree_df


def network_in_out_degree(g, output):
    '''
    Given a graph in nx, it returns a df with nodes indegree and outdegree and it saves it in output
    '''

    # in and out degree
    indegree_dict = dict(g.in_degree(weight='weight'))
    outdegree_dict = dict(g.out_degree(weight='weight'))

    for node, indegree in indegree_dict.items():
        print(f"Node {node}: Indegree (with weights) {indegree}")
    for node, outdegree in outdegree_dict.items():
        print(f"Node {node}: Outdegree (with weights) {outdegree}")


    # degree df for viualization
    node_list = indegree_dict.keys()

    degree_df = pd.DataFrame(columns=['node', 'outdegree', 'indegree'], index=node_list)

    for node, indegree in indegree_dict.items():
        degree_df.at[node, 'indegree'] = indegree
    for node, outdegree in outdegree_dict.items():
        degree_df.at[node, 'outdegree'] = outdegree

    degree_df['total degree'] = degree_df['indegree'] + degree_df['outdegree']

    # save degree df
    degree_df.to_csv(output, index=False)




# network measures


# degree centrality

def degree_centrality(g):
    '''
    Compute degree centrality of network g in nx
    '''
    
    return nx.degree_centrality(g)


# HITS - hubs and authorities

def hubs_authorities(g, col_node, col_value, file_hub, file_auth):
    '''
    Compute hubs and authorities of network g in nx
    g: network
    col_node: column of final df containing name of nodes
    col_value: column of hubs/authorities value
    file_hub: path to file where to save hubs values
    file_auth: path to file where to save authorities values
    '''

    columns = [col_node, col_value]

    h, a = nx.hits(g)

    df_hub = write_dict_to_df(h, columns)
    df_hub = df_hub.sort_values(by=[columns[1]], ascending=False)
    df_hub.to_csv(file_hub, index=False)
    print(h)
    print(a)
    print('\n\n\n')

    df_auth = write_dict_to_df(a, columns)
    df_auth = df_auth.sort_values(by=[columns[1]], ascending=False)
    df_auth.to_csv(file_auth, index=False)
    

# closeness centrality

def closeness_centrality(g, columns, output_file):
    '''
    Compute closeness centrality of network g in nx
    '''

    closeness_centrality = nx.closeness_centrality(g)
    df_closeness = write_dict_to_df(closeness_centrality, columns)
    df_closeness = df_closeness.sort_values(by=[columns[1]], ascending=False)
    df_closeness.to_csv(output_file, index=False)
    
    return closeness_centrality


# betweenness centrality

def betweenness_centrality(g, columns, weighted, weight_column, output_file):
    '''
    Compute betweenness centrality of network g in nx
    '''

    if weighted:
        betweenness_centrality = nx.betweenness_centrality(g, weight=weight_column)
    else:
        betweenness_centrality = nx.betweenness_centrality(g)
    print(betweenness_centrality)
    df_betweenness = write_dict_to_df(betweenness_centrality, columns)
    df_betweenness = df_betweenness.sort_values(by=[columns[1]], ascending=False)
    df_betweenness.to_csv(output_file, index=False)
    
    return betweenness_centrality


# eigenvector centrality

def eigenvector_centrality(g, columns, output_file):
    '''
    Compute eigenvector centrality of network g in nx
    '''

    eigenvector_centrality = nx.eigenvector_centrality(g)
    df_eigenvector = write_dict_to_df(eigenvector_centrality, columns)
    df_eigenvector = df_eigenvector.sort_values(by=[columns[1]], ascending=False)
    df_eigenvector.to_csv(output_file, index=False)

    return eigenvector_centrality


# clustering coefficient

def clustering_coefficient(g, weighted, weight_attr, output_file):
    '''
    Compute clustering coefficient of network g in nx
    - weighted: True/False if network is/is not weighted
    - weight_attr: name of edges weight attribute in the network
    '''

    if weighted:
        clustering_coefficient = nx.average_clustering(g, weight=weight_attr)
    else:
        clustering_coefficient = nx.average_clustering(g)
    
    with open(output_file, 'a') as f:
        f.write('CLustering coefficient: ' + str(clustering_coefficient))

    return clustering_coefficient


# density

def density(g, output_file):
    '''
    Compute density of network g in nx
    '''

    density = nx.density(g)

    with open(output_file, 'w') as f:
        f.write('Density: ' + str(density))

    return density

#betweenness_centrality(network, ['node', 'betweenness'], output_dir_8+'betweenness_8.csv')


# shortest path

def shortest_path(g, output_file):
    '''
    Compute shortest path between all the nodes
    '''

    shortest_path = nx.all_pairs_all_shortest_paths(g)

    return shortest_path

'''sp = shortest_path(g, 'prova')
while True:
    try:
        print(sp.next())'''




# NB: VERIFIED THAT FUNCTIONS gini_index AND gini RETURN EQUIVALENT RESULTS

def gini_index(distribution):
    '''
    Compute gini index of a distribution
    '''

    # Ensure the distribution is a numpy array
    distribution = np.array(distribution)
    
    # Number of elements
    n = len(distribution)
    
    # Mean of the distribution
    mean = np.mean(distribution)
    #print('mean', mean)
    
    # Gini calculation
    gini_sum = 0
    for i in range(n):
        for j in range(n):
            gini_sum += np.abs(distribution[i] - distribution[j])
    
    gini_index = gini_sum / (2 * n**2 * mean)

    return gini_index


def gini(series_of_values):
    '''
    Compute gini index of a distribution
    '''
    
    sorted_list = sorted(series_of_values.fillna(0))
    height, area = 0, 0
    for value in sorted_list:
        height += value
        area += height - value / 2.
    fair_area = height * len(sorted_list) / 2.
    if fair_area == 0:
        return np.nan
    return (fair_area - area) / fair_area




# functions to compute F1 for similarity between communities in different networks (partitions) -> BCubed paper -> https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0256175

def jaccard(set1, set2):
    '''
    Compute jaccard index between two sets
    '''

    jaccard = len(set1.intersection(set2)) / len(set1.union(set2))

    return jaccard


def f1_similarity_diff(set1, set2):
    '''
    Compute F1 similarity when we have some overlapping and some non-overlapping nodes in the two partitions -> max F1
    set1, set2 : sets of nodes resectively in the first and second partitions
    '''

    jac = jaccard(set1, set2)
    f1 = (2 * jac) / (1 + jac)

    return f1


def precision_n(l_community, c_community):
    '''
    Compute precision for node n
    l_community : 'ground truth' community (first one) node n belongs to
    c_community : detected community of node n (second one) node n belongs to
    '''

    return len(l_community.intersection(c_community)) / len(c_community)


def recall_n(l_community, c_community):
    '''
    Compute precision for node n
    l_community : 'ground truth' community (first one) node n belongs to
    c_community : detected community of node n (second one) node n belongs to
    '''

    return len(l_community.intersection(c_community)) / len(l_community)


def search_el(el, list_of_sets):
    '''
    Given an element and a list of sets, find the set where this element falls into
    '''
    
    found = False
    num_set = 0
    res = []

    while (found == False) and (num_set < len(list_of_sets)):
        if el in list_of_sets[num_set]:
            found = True
            res = list_of_sets[num_set]
        else:
            num_set += 1
    
    return res
    

def precision_recall_c_l(c, l):
    '''
    Compute precision and recall for the core-F1, where pair of network partitions consist of same set of nodes
    '''
    
    sum_precision = 0
    sum_recall = 0

    len_c = 0
    len_l = 0

    for set in c:
        len_c += len(set)
    for set in l:
        len_l += len(set)

    for set_c in c:
        for el in set_c:
            set_l = search_el(el, l)
            sum_precision += precision_n(set_l, set_c)
            sum_recall += recall_n(set_l, set_c)
    
    precision = 1 * sum_precision / len_c
    recall = 1 * sum_recall / len_l

    return precision, recall


def f1_similarity_eq(c, l):
    '''
    Compute core-F1, where pair of network partitions consist of same set of nodes
    '''
    
    precision, recall = precision_recall_c_l(c, l)
    f1 = (2*precision*recall) / (precision+recall)

    return f1

    

if __name__ == "__main__":
    
    '''g = nx.read_graphml('participants organizations/network nx/org_network_weighted_9.graphml')
    output_dir = 'participants organizations/centrality/9/'

    hubs_authorities(g, 'organization', 'value', output_dir + 'hubs.csv', output_dir + 'authorities.csv')'''


    '''network_degree(g, output_dir+'degree_tot.csv')
    closeness_centrality(g, ['country', 'value'], output_dir+'closeness.csv')
    betweenness_centrality(g, ['country', 'value'], True, 'weight', output_dir+'betweenness.csv')
    clustering_coefficient(g, True, 'weight', output_dir+'measures.txt')
    density(g, output_dir+'measures.txt')'''


#g = nx.read_graphml('participants/graph nx/coord participant no self only efta indirected/9_graph.graphml')
#output_dir = 'participants/centrality/coord participant only efta indirected/9/'
#output_dir_8 = 'project_nlp_net/network_weighted_topics_NEW/network measures/h2020/'

'''g = network
print('Nodes')
print(g.nodes(data=True))
print('Edges')
print(g.edges(data=True))
print(len(g.nodes()))
print(len(g.edges()))'''    