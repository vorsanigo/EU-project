import pandas as pd


# recursive utility to collect all leaf topics under a parent node
def get_leaves(node):
    if node not in children_map:
        return [node]
    left, right = children_map[node]
    return get_leaves(left) + get_leaves(right)


# ensure we pick top-most parents (avoid nested/overlapping selections)
def has_ancestor_in_set(node, parents_set):
    p = child2parent.get(node)
    while p is not None:
        if p in parents_set:
            return True
        p = child2parent.get(p)
    return False
    


if __name__ == "__main__":

    # umap hdbscan parameters
    umap_components = 2
    hdbscan_param = 50

    # paths
    # hierarchy csv
    dir_topics = '../embeddings_topics/description_topics/'
    hier_csv = dir_topics + 'umap_' + str(umap_components) + '_hdbscan_' + str(hdbscan_param) + '/hierarchical_topics.csv'
    info_topics = dir_topics + 'umap_' + str(umap_components) + '_hdbscan_' + str(hdbscan_param) + '/info_topic_umap_' + str(umap_components) + 'hdbscan_' + str(hdbscan_param) + '.csv'
    # output dir
    hier_output_dir = dir_topics + 'umap_' + str(umap_components) + '_hdbscan_' + str(hdbscan_param) + '/merged_topics/'

    # threshold for merging
    threshold = 1.2


    # 1) get the hierarchical merges df and original topics df

    hier = pd.read_csv(hier_csv)
    original_topics = pd.read_csv(info_topics)


    # 2) build parent->(left,right) map and child->parent map

    children_map = {}
    child2parent = {}
    for _, row in hier.iterrows():
        parent = int(row["Parent_ID"])
        left = int(row["Child_Left_ID"])
        right = int(row["Child_Right_ID"])
        children_map[parent] = (left, right)
        child2parent[left] = parent
        child2parent[right] = parent

    print(children_map)
    print(child2parent)


    # 3) choose a distance threshold (tune this; higher -> fewer, coarser macrotopics)

    parents_below = [int(r["Parent_ID"]) for _, r in hier.iterrows() if r["Distance"] <= threshold]

    selected_parents = [p for p in parents_below if not has_ancestor_in_set(p, set(parents_below))]

    print('\n')
    print('selected parents', selected_parents)
    print('\n')


    # 4) build groups to merge (list of lists of ORIGINAL topic ids)

    groups = []

    for p in selected_parents:
        leaves = sorted(set(get_leaves(p)))
        # often leave out outlier -1 topics unless you explicitly want to merge them
        leaves = [l for l in leaves if l != -1]
        if len(leaves) > 1:
            groups.append(leaves)

    print("Will merge groups (examples):", groups[:10])


    # 5) add, if there are any, topics that were left as singleton, not merged with any other new macrotopic

    flatten_groups = [x for sublist in groups for x in sublist]
    print('s1', set(flatten_groups))
    print('s2', set(list(original_topics['Topic'])))
    not_in_groups = set(list(original_topics['Topic'])) - set(flatten_groups)
    print(not_in_groups)
    
    if -1 in not_in_groups:
        not_in_groups.remove(-1)

    not_in_groups_lists = [[x] for x in not_in_groups]
    original_topics_filtered = original_topics[original_topics['Topic'].isin(not_in_groups)]
    original_topics_filtered['merged_topics'] = not_in_groups_lists
    original_topics_filtered = original_topics_filtered.rename(columns={'Topic': 'Parent_ID', 'Name': 'Parent_Name'})
    original_topics_filtered_col = original_topics_filtered[['Parent_ID', 'Parent_Name', 'merged_topics']]

    print('original', original_topics_filtered_col)


    # 6) select rows in the hierarchical topics df according to the threshold by filtering by the selected parents eand add corresponding group with initial topics ids

    hier_threshold = hier[hier["Parent_ID"].isin(selected_parents)]
    hier_threshold['merged_topics'] = groups #+ not_in_groups_lists


    # 7) compbine new merged topics and orginial topics

    hier_tot = pd.concat([hier_threshold, original_topics_filtered_col]).reset_index()
    hier_tot['Representation'] = ''


    # 8) create column with keywords of the merged topics

    for i in range(len(hier_tot)):
        if not(pd.isna(hier_tot.at[i, 'Child_Left_ID'])) and not(pd.isna(hier_tot.at[i, 'Child_Left_ID'])):  # this is an original topic, not a merged one
            print(hier_tot.at[i, 'Child_Left_ID'])
            left_words = hier_tot.at[i, 'Child_Left_Name'].split('_')
            right_words = hier_tot.at[i, 'Child_Right_Name'].split('_')
            tot_words = left_words + right_words
            tot_words = list(set(tot_words))
            hier_tot.at[i, 'Representation'] = tot_words
        else:  # this is a merged topic, get the keywords from the original topics
            tot_words = hier_tot.at[i, 'Parent_Name'].split('_')
            hier_tot.at[i, 'Representation'] = tot_words[1:]


    # 9) save merged topics df
    hier_tot.to_csv(hier_output_dir + 'merged_topics_' + str(threshold) + '.csv', index=False)