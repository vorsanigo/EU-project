# Functions to create network graphs
# NB: to save the graph -> .graphml

import networkx as nx
import graph_tool as gt
import pandas as pd
import polars as pl



def create_edgelist_undirected(df, id_group_column, list_to_edge_column, alias_list_to_edge_column, source_column, target_column, output_file):
    '''
    Given a dataframe with a column containing lists of nodes (with eventually additional columns) that have to be linked (undirected edgelist to be created), it returns the corresponding edgelist and saves it to a file
    Eg: df format (edgelist of organizations collaboration on same project): projectRcn | org_id -> 12345 | [123, 456, 789]  
    file_df: file name of polars dataframe
    list_to_edge_column: str, name of the column containing lists of nodes to be linked
    alias_list_to_edge_column: str, alias for the column containing lists of nodes to be linked
    source_column: str, name of the column to be used as source in the edgelist
    target_column: str, name of the column to be used as target in the edgelist
    output_file: str, name of the output file where the edgelist will be saved -> source | target -> 123 | 456
                                                                                                     123 | 789
                                                                                                     456 | 789
    '''

    # create edgelist

    edge_list = (
    df.with_columns(pl.col(list_to_edge_column).alias(alias_list_to_edge_column)) # create copy of column to explode
    .explode(pl.col(list_to_edge_column)) # explode copy of the column to explode
    .with_columns(pl.cum_count(id_group_column).over(id_group_column).alias("list_index") - 1) # cumulative sum over column that indicates the group of nodes to be linked (eg: project id if we created the edgelist of organizations collaborating on the same project)
    #.with_columns(pl.col(alias_list_to_edge_column).alias(alias_list_to_edge_column + "_copy")) # create copy of the column containing nodes to be linked
    #.drop(list_to_edge_column)
    #.drop(list_to_edge_column + "_copy") # drop original column
    .with_columns(pl.col(alias_list_to_edge_column).list.head(pl.col("list_index"))) # take the alias column of the one of the nodes to be linked and keep only the first n elements, where n is the value of the cumulative sum over the column that indicates the group of nodes to be linked
    # this is useful bcs we do not want to link the node with itself, but only with the other nodes in the group and we do not want x -> x, x -> y and y -> x, but only x -> y
    .drop("list_index") # drop the cumulative sum column
    .explode(alias_list_to_edge_column) # explode to have the combinations of nodes to be linked
    .drop_nulls(alias_list_to_edge_column) # drop null
    .rename({list_to_edge_column: source_column, alias_list_to_edge_column: target_column}) # rename columns to have source - target names
    )
    
    #edgelist = edge_list.to_pandas()  # convert to pandas dataframe for easier handling
    print(edge_list)

    # save df edgelist
    edge_list.write_csv(output_file)

    return edge_list



def edgelist_weighted_undirected(edgelist, source_col, target_col, new_source_col, new_target_col):
    '''
    Given the edgelist with all the entries in every order, it groups them without considering their order and counts how many times they appear
    edgelist: edgelist obtained through function create_edgelist_undirected
    source_col: source column in edgelist
    target_col: target column in edgelist
    new_source_col: new name for source
    new_target_col: new name for target
    '''

    # normalize pairs by sorting (min, max)
    edgelist_weighted_undirected = edgelist.with_columns([
        pl.min_horizontal(source_col, target_col).alias('node1'),
        pl.max_horizontal(source_col, target_col).alias('node2'),
    ])

    # group by normalized edge and count
    edgelist_weighted_undirected_final = (
        edgelist_weighted_undirected.group_by(['node1', 'node2'])
        .len()
        .rename({"len": "weight", 'node1': new_source_col, 'node2': new_target_col})
        .sort("count", descending=True)
    )

    return edgelist_weighted_undirected_final

    # remove duplicated pairs -> project id and organization id
    '''df = df.unique(subset=[proj_column, org_id_column])

    # group by project and aggregate organization ids and names into lists
    grouped_df = df.group_by(proj_column).agg(pl.col(org_id_column), pl.col(org_name_column))

    print(grouped_df)

    # create collaboration links between organizations by computing combinations of organizations per each project
    grouped_df = grouped_df.with_columns(
        pl.col(org_id_column).map_elements(lambda x: list(itertools.combinations(x, 2))).alias("edges"),
    )
    
    print(grouped_df)

    # explode the edges column to create a row for each edge
    grouped_df = grouped_df.explode("edges")
    grouped_df = grouped_df.with_columns(
        #pl.col(org_id_column).alias("org_ids")
        pl.col("edges").map_elements(lambda x: x[0]).alias("source"),
        pl.col("edges").map_elements(lambda x: x[1]).alias("target")
    )
    print(grouped_df)

    # drop null, the ones that have projects by themselves -> no collaboration link
    grouped_df = grouped_df.drop_nulls()

    # drop not useful columns
    grouped_df = grouped_df.drop([org_id_column, org_name_column, 'edges'])
    
    # save df
    grouped_df.write_csv(output_file)
    '''



def create_network_nx(edgelist, nodes_attr, network_type, output_file):
    '''
    Given edgelist (with edges attributes), nodes attributes, network type, and name of output file, it creates and saves the nnetwork graph
    Format of edgelist: [('fr', 'it', {"weight": 5, 'name': 'cool'}), ('fr', 'it', {"weight": 10, 'name': 'wow'}), ('it', 'es', {"color": "red", 'name': 'chulo'})]
    Format of nodes attributes: {'fr': {'name': 'france', 'pop': 100}, 'it': {'name': 'italy', 'pop': 90}, 'es': {'name': 'spain', 'pop': 80}}
    Types of networks: directed, undirected, multiedge_directed, multiedge_undirected
    '''
    
    # types of networks
    if network_type == 'directed':
        g = nx.DiGraph()
    elif network_type == 'undirected':
        g = nx.Graph()
    elif network_type == 'multiedge_directed':
        g = nx.MultiDiGraph()
    elif network_type == 'multiedge_undirected':
        g = nx.MultiGraph()
    
    # set edgelist
    g.add_edges_from(edgelist)
        
    # set nodes attributes
    nx.set_node_attributes(g, nodes_attr)

    # save graphs
    nx.write_graphml(g, output_file)
    
    print('Network created')
        


def df_edgelist_to_list_edgelist(df, source_col, target_col, edge_properties_cols):
    '''Given edgelist in dataframe with edges attributes, it returns the corresponding edgelist in a list format
    df format: source | target | prop_1 | prop_2 | ...
    source_col: str
    target col: str
    edge_properties_col: list of str
    '''
    
    edgelist = []
    
    for i in range(len(df)):
        source = df.at[i, source_col]
        target = df.at[i, target_col]
        attr = {}
        for col in edge_properties_cols:
            attr[col] = df.at[i, col]
        edgelist += [(source, target, attr)]
    
    return edgelist



def list_edgelist_to_df_edgelist(list_edges):
    '''Given edgelist in list with edges attributes, it returns the corresponding edgelist in a dataframe format
    edgelist format: [('fr', 'it', {"weight": 5, 'name': 'cool'}), ('fr', 'it', {"weight": 10, 'name': 'wow'}), ('it', 'es', {"color": "red", 'name': 'chulo'})]
    '''
    
    df = pd.DataFrame()
    
    for i in range(len(list_edges)):
        source = list_edges[i][0]
        target = list_edges[i][1]
        dict_to_add = {}
        dict_to_add['source'] = source
        dict_to_add['target'] = target
        for key, value in list_edges[i][2].items():
            dict_to_add[key] = value
        df = df._append(dict_to_add, ignore_index=True)
    
    return df    
    
 

def df_nodes_to_dict_nodes(df, node_col, node_attr_cols):
    '''Given nodes in dataframe with their attributes, it returns the corresponding dictionary
    df format: node | attr_1 | attr_2 | ...
    node_col: str
    node_attr_col: list of str
    '''
     
    dict_attr_nodes = {}
     
    for i in range(len(df)):
        dict_attr = {}
        for col in node_attr_cols:
            dict_attr[col] = df.at[i, col]
        dict_attr_nodes[df.at[i, node_col]] = dict_attr
        
    return dict_attr_nodes
        


def dict_nodes_to_df_nodes(dict_nodes):
    '''Given nodes in dataframe with their attributes, it returns the corresponding dictionary
    dictionary format: {'fr': {'name': 'france', 'pop': 100}, 'it': {'name': 'italy', 'pop': 90}, 'es': {'name': 'spain', 'pop': 80}}S
    '''
    
    df = pd.DataFrame()
    
    for key, value in dict_nodes.items:
        dict_to_add = {}
        dict_to_add['node'] = key
        for attr_name, attr_value in value:
            dict_to_add[attr_name] = attr_value
        df = df._append(dict_to_add, ignore_index=True)
    
    return df
 


# EXAMPLES

# Example create_network_nx
'''
# edgelist (with edges attributes) and nodes attributes
edgelist = [('fr', 'it', {"weight": 5, 'name': 'cool'}), ('fr', 'it', {"weight": 10, 'name': 'wow'}), ('it', 'es', {"color": "red", 'name': 'chulo'})]
nodes_attr = {'fr': {'name': 'france', 'pop': 100}, 'it': {'name': 'italy', 'pop': 90}, 'es': {'name': 'spain', 'pop': 80}}

# create network
create_network_nx(edgelist, nodes_attr, 'multiedge_undirected', 'prova_nx.graphml')
print('done')'''

# read network -> networkx
'''g = nx.read_graphml('ERC projects/project_countries/efta/network_country_coord_part_dir_7_efta.graphml')
print('Nodes')
print(g.nodes(data=True))
print('Edges')
print(g.edges(data=True))
print(len(g.nodes()))
print(len(g.edges()))'''

'''# read network graph_tool
g = gt.load_graph('prova_nx.graphml')
for v in g.vertices():
    print(f"Node {int(v)}:")
    for prop_name, prop in g.vp.items():
        print(f"  {prop_name}: {prop[v]}")
print("Edge Properties:")
for prop_name, prop_map in g.ep.items():
    print(f"Property: {prop_name}")
    for e in g.edges():
        print(f"Edge {e}: {prop_name} = {prop_map[e]}")
'''

'''df_edgelist = pd.read_csv('participants/edgelist enriched/coord participant no self only efta indirected/9.csv')
#df_edgelist = df_edgelist.rename(columns={'count_topics_links': 'weight'})
edgelist = df_edgelist_to_list_edgelist(df_edgelist, 'source iso 2', 'target iso 2', ['weight'])
#print(edgelist)
create_network_nx(edgelist, {}, 'undirected', 'participants/graph nx/coord participant no self only efta indirected/9_graph.graphml')'''

'''g = nx.read_graphml('participants/graph nx/coord participant no self only efta indirected/9_graph.csv')
print('Nodes')
print(g.nodes(data=True))
print('Edges')
print(g.edges(data=True))
print(len(g.nodes()))
print(len(g.edges()))'''

#print(df_edgelist)
'''df_edgelist_efta = pd.read_parquet('ERC projects/project_countries/country_edgelist_7_efta.parquet')
edgelist = df_edgelist_to_list_edgelist(df_edgelist_efta, 'list_country_x', 'list_country_y', ['projectRcn'])
print(edgelist)
create_network_nx(edgelist, {}, 'directed', 'ERC projects/project_countries/network_country_coord_part_dir_7_efta.graphml')'''

'''df_edgelist_coord = pd.read_csv('participant organization/edgelist enriched/coord participant no self/7_coord_part_name_efta.csv')

edgelist = df_edgelist_to_list_edgelist(df_edgelist_coord, 'source', 'target', ['weight'])

df_source = df_edgelist_coord[['source', 'country_code_x', 'city_nominatim_x']]
df_target = df_edgelist_coord[['target', 'country_code_y', 'city_nominatim_y']]
df_source = df_source.rename(columns={'source': 'node', 'country_code_x': 'country_code', 'city_nominatim_x': 'city_nominatim'})
df_target = df_target.rename(columns={'target': 'node', 'country_code_y': 'country_code', 'city_nominatim_y': 'city_nominatim'})
df_tot = pd.concat([df_source, df_target])
df_tot = df_tot.drop_duplicates(ignore_index=True)
nodes_attr = df_nodes_to_dict_nodes(df_tot, 'node', ['country_code', 'city_nominatim'])


create_network_nx(edgelist, nodes_attr, 'directed', 'participant organization/graph nx new/org_participant_7_efta.graphml')'''

'''df_topics = pd.read_csv('topics/umap_15_hdbscan_100/info_topic_umap_15hdbscan_100_NEW.csv')
nodes_attr = df_nodes_to_dict_nodes(df_topics, 'Topic', ['Name'])
df_edgelist = pd.read_csv('project_nlp_net/edgelist_weighted_topics/h2020.csv')
df_edgelist = df_edgelist.rename(columns={'count_links': 'weight'})
edgelist = df_edgelist_to_list_edgelist(df_edgelist, 'topic_source', 'topic_target', ['weight'])
create_network_nx(edgelist, nodes_attr, 'undirected', 'project_nlp_net/network_weighted_topics/undirected_weighted_h2020.graphml')'''

'''
   
# graph_tool

def create_network_gt(edgelist, network_type, nodes_attr, edges_attr, output_file):
    
    if (network_type == 'directed') or (network_type == 'multi_directed'):
        g = gt.Graph(directed=True)
    elif (network_type == 'undirected') or (network_type == 'multi_directed'):
        g = gt.Graph(directed=False)
    
    weight = g.new_ep('int')
    node_names = g.add_edge_list(edgelist, hashed=True, eprops=[weight])
    name_property = g.new_vertex_property("string")  # For node names
    
    dict_node_prop = {}
    for name_prop, type_prop in nodes_attr:
        dict_node_prop[name_prop] = g.new_vertex_property(type_prop)
    
    for node in range(g.num_vertices()):
        name_property[node] = node_names[node] 
        for name_prop, gt_name_prop in dict_node_prop:
            print(node, node_names[node])
            # Assign the attributes to each vertex
            #for name, attributes in nodes_attr.items():
            #attributes["name"]
            gt_name_prop[node] = nodes_attr[node_names[node]][name_prop]
            #city_property[node] = nodes_attr[node_names[node]]["city"]

    print('\n\n')
    print(weight.fa)
    
    for name_prop, gt_name_prop in dict_node_prop:
        g.vertex_properties[name_prop] = gt_name_prop
        

    
    g.edge_properties['weight'] = weight
    
    # save graph
    g.save(output_file)'''


'''df = pl.DataFrame({
    "source": ['fr', 'it', 'it', 'de', 'it', 'gb'],
    "target": ['it', 'fr', 'fr', 'it', 'de', 'it'],
})



e = edgelist_weighted_undirected(df, 'source', 'target', 'node1', 'node2')
print(e)'''



'''for i in range(1, 10):
    df_edgelist = pd.read_csv('gravity model/gravity results/collaboration_pop_gdp_distance/estimated collaborations/est_' + str(i) + '.csv')
    edgelist = df_edgelist_to_list_edgelist(df_edgelist, 'source', 'target', ['weight'])
    create_network_nx(edgelist, {}, 'undirected', 'gravity model/gravity results/collaboration_pop_gdp_distance/estimated networks/' + str(i) + '_graph.graphml')'''