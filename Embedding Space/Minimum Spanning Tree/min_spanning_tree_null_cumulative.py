# Script to compute min spanning tree
# we create sparse matrix using knn instead of computing the complete matrix of pairwise distances

import polars as pl
import pandas as pd
from pathlib import Path
from datetime import date
import os
import time
import networkx as nx
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
import polars as pl
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pickle
import numpy as np
from sklearn.neighbors import NearestNeighbors, kneighbors_graph
from scipy.sparse.csgraph import connected_components
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial import Delaunay
from itertools import combinations
from scipy.spatial import ConvexHull, Delaunay, distance_matrix
from min_spanning_tree_fun import *



# we compute it for:
# 1) time windows on total data

# ## Framework programmes
# 
# - FP1: 1984-1987
# - FP2: 1987-1991
# - FP3: 1990-1994
# - FP4: 1994-1998
# - FP5: 1998-2002
# - FP6: 2002-2006
# - FP7: 2007-2013
# - H2020: 2014-2020
# - Horizon Europe: 2021-2027


### SET 

# set directory
cwd = Path.cwd()
parent_dir = cwd.parent.parent

# data dir
data_dir = parent_dir / 'Data'



mst_type = 'window tot'
# 'window tot'

# number of iterations to repeat experiment
num_iter = 1

# choose data sample
# 'real_tot' -> if bounding box determined by all the data points
# 'real_sub' -> if bounding box determined by data points in the subset of the mst
sample_size = 'real_sub'

# sampling type
# bounding_box -> with embeddings bcs too big for convex hull
# convex_hull -> with reduced embeddings
sampling = 'bounding_box' 

# embeddings column -> total or reduced
embeddings_col = 'emb_list' # 'red_emb_list

# umap or PCA parameter -> dimensionality
components = 768

# choose if total embeddings or umap or pca reduced embeddings
# umap
# pca
# no_red_emb
red_emb_type = 'no_red_emb'

# choose how many points we need minimum to run MST
if embeddings_col == 'emb_list':
    points_threshold = 2
elif components <= 10:
    points_threshold = components
else: points_threshold = 2


# embeddings
emb = np.load('embeddings_topics/description embeddings/bge_1024dim.npy')#specter2_768dim_NORM.npy embeddings_description.npy
if red_emb_type == 'umap':
    red_emb = np.load('embeddings_topics/description embeddings/red_emb_umap_' + str(components) + '.npy')
elif red_emb_type == 'pca':
    red_emb = np.load('embeddings_topics/PCA reduced embeddings/red_emb_' + str(components) + '.npy')

# nromalization
# normalized
# abs
norm = 'normalized'

# set output dir according to data sample
# min spanning tree/knn null model convex hull norm/ -> if red embeddings -> convex hull
# min spanning tree/knn null model bounding box norm/ -> if embeddings -> bounding box
if red_emb_type == 'umap':
    output_dir = 'min spanning tree/knn null model ' + sampling + ' norm ' + str(components) + ' umap/'
elif red_emb_type == 'pca':
    output_dir = 'min spanning tree/knn null model ' + sampling + ' norm ' + str(components) + ' PCA/'
elif red_emb_type == 'no_red_emb':
    output_dir = 'min spanning tree/knn null model ' + sampling + ' norm tot emb CUMULATIVE/' 



### PREPARE DATA

# 1) projects df

proj_dir = data_dir

list_beginning = [1984, 1987, 1990, 1994, 1998, 2002, 2007, 2014, 2021]
list_end = [1987, 1991, 1994, 1998, 2002, 2006, 2013, 2020, 2027]

list_df = []

#for i in range(1, 10):

df = pl.read_csv(proj_dir / 'project_until_2025_no_nan_obj.csv')

df = df.with_columns(pl.Series(embeddings_col, list(emb)))

df_clean = df.filter(pl.col('startDate').is_not_null())

df_sorted = df_clean.sort('startDate')
df_sorted = df_sorted.with_columns(
    pl.col('startDate').str.strptime(pl.Date, '%Y-%m-%d').alias('start_date'),
    pl.col('endDate').str.strptime(pl.Date, '%Y-%m-%d').alias('end_date')
)

for i in range(len(list_beginning)):
    start = date(list_beginning[i], 1, 1)
    end = date(list_end[i], 12, 31)
    end_2 = date(list_end[i] + 2, 12, 31)
    fp = i + 1
    df_fp = df_sorted.filter((pl.col('fp') == fp))
    df_before = df_sorted.filter((pl.col('fp') == fp) & (pl.col('start_date') < start))
    df_after = df_sorted.filter((pl.col('fp') == fp) & (pl.col('start_date') > end))
    df_after_2 = df_sorted.filter((pl.col('fp') == fp) & (pl.col('start_date') > end_2))
    print('FP:', str(fp))
    print('Size df:', len(df_fp))
    print('Number projects before start:', str(len(df_before)))
    print('Number projects after end:', str(len(df_after)))
    print('Number projects after 2 years since end:', str(len(df_after_2)))
    print('\n')

# organizations dir
org_dir = data_dir / 'organizations/'


# organizations df

org_df = pl.read_csv(data_dir / 'org_until_2025.csv' ,infer_schema_length=0, dtypes={"colname": pl.Utf8})

# efta countries

efta_df = pl.read_csv(data_dir / 'efta countries.csv')
efta_df = efta_df.with_columns(pl.col('country').str.to_lowercase())
efta_countries = efta_df['country'].to_list()


# Merge proj + embeddings

#proj_emb_df = df_sorted.join(emb_df, on=['id', 'fp'], how='left')
proj_emb_df = df_sorted[['id', 'fp', embeddings_col, 'start_date', 'end_date']]
for i in range(len(list_beginning)):
    start = date(list_beginning[i], 1, 1)
    end = date(list_end[i], 12, 31)
    end_2 = date(list_end[i] + 2, 12, 31)
    fp = i + 1
    df_fp = proj_emb_df.filter(pl.col('fp') == fp)
    df_before = proj_emb_df.filter((pl.col('fp') == fp) & (pl.col('start_date') < start))
    df_after = proj_emb_df.filter((pl.col('fp') == fp) & (pl.col('start_date') > end))
    df_after_2 = proj_emb_df.filter((pl.col('fp') == fp) & (pl.col('start_date') > end_2))
    print('FP:', str(fp))
    print('Size df:', str(len(df_fp)))
    print('Number projects before start:', str(len(df_before)))
    print('Number projects after end:', str(len(df_after)))
    print('Number projects after 2 years since end:', str(len(df_after_2)))
    print('\n')


# 5) Extract total points

points_tot = [np.array(x) for x in proj_emb_df[embeddings_col].to_list()]
points_tot = np.array(points_tot, dtype=float)


### COMPUTE MST

## 1) time windows on total data

if mst_type == 'window tot':
    
    # time windows
    window_size = 12  # months
    step = 12       # months
    
    # start and end date
    start_date = date(1983, 1, 1) #df["start_date"].min()
    end_date = date(2025, 12, 31) #df["end_date"].max()


    # windows type dir
    window_type_dir = 'window_' + str(window_size) + '_step_' + str(step) + '/'

    # plot dir
    output_plot_dir = Path(output_dir + window_type_dir + 'plot window tot_' + embeddings_col)
    output_plot_dir.mkdir(parents=True, exist_ok=True)
    output_plot_path = output_dir + window_type_dir + 'plot window tot_' + embeddings_col + '/'

    # create output country dir
    output_mst_len_dir = Path(output_dir + window_type_dir + 'mst len window tot_' + embeddings_col)
    output_mst_len_dir.mkdir(parents=True, exist_ok=True)
    output_mst_len_path = output_dir + window_type_dir + 'mst len window tot_' + embeddings_col + '/'


    # create output windows time dir
    output_windows_dir = Path(output_dir + window_type_dir + 'windows time tot_' + embeddings_col)
    output_windows_dir.mkdir(parents=True, exist_ok=True)
    output_windows_path = output_dir + window_type_dir + 'windows time tot_' + embeddings_col + '/'


    start = time.time()


    # repeat experiment 100 times to average out randomness
    for i in range(num_iter):

        count = 1

        # start and end date
        start_date = date(1983, 1, 1) #df["start_date"].min()
        end_date = date(2025, 12, 31) #df["end_date"].max()

        # initialization
        current_start = start_date
        current_end = start_date
        windows_list = []
        results_graphs = []
        results_lengths = []
        length_list = []

        while current_end <= end_date:

            
            print("# window: ", str(count) + "/" + str(86))


            current_end = current_end + relativedelta(months=window_size)
            
            window_df = proj_emb_df.filter(
                (pl.col("start_date") >= start_date) & 
                (pl.col("start_date") < current_end)
            )

            # extract points from embeddings
            points_real = [np.array(x) for x in window_df[embeddings_col].to_list()]
            points_real = np.array(points_real, dtype=float)

            # points dimensionality
            dim = points_real.shape[1]
            
            if len(points_real) > points_threshold:
                if sampling == 'bounding_box':
                    if sample_size == 'real_tot':
                        points = sample_points_in_bounding_box(points_tot, points_real.shape)
                    else:
                        points = sample_points_in_bounding_box(points_real, points_real.shape)
                elif sampling == 'convex_hull':
                    if sample_size == 'real_tot':
                        points = sample_points_in_convex_hull(points_tot, len(points_real))
                    else:
                        points = sample_points_in_convex_hull(points_real, len(points_real))
            else:
                points = np.array([])


            chosen_k, comp_results = find_min_k_for_connectivity(points)

            # Build sparse graph (each node connected to k nearest neighbors)
            k = chosen_k
            knn_graph = kneighbors_graph(points, n_neighbors=k, mode='distance', include_self=False)  
            knn_graph = knn_graph.maximum(knn_graph.T)
            #print('Num components:', connected_components(knn_graph))  
            
            # compute min spanning tree
            mst = minimum_spanning_tree(knn_graph)
            print(f"Number of edges in MST: {mst.nnz}")
            print(f"Total MST length: {mst.sum()}")

            if mst != None:
                length_list += [mst.sum() / (len(points_real)**((dim-1)/dim))] 
                #length_list += [mst.sum()]
                windows_list += [current_end - relativedelta(months=window_size)] 
                
            count += 1

        if i == 0:
            with open(output_windows_path + 'windows.pkl', 'wb') as f:
                pickle.dump(windows_list, f)
            f.close()
            lengths_arrays = [length_list]
        
        else:
            lengths_arrays.append(length_list)

        with open(output_mst_len_path + 'mst_len_' + str(i) + '.pkl', 'wb') as f:
            pickle.dump(length_list, f)
        f.close()

    end = time.time()
    print(lengths_arrays)
    lengths_arrays = np.array(lengths_arrays)
    
    mean_length_list = np.mean(lengths_arrays, axis=0) #sum_arrays / num_iter
    std_lenght_list = np.std(lengths_arrays, axis=0)
    
    with open(output_mst_len_path + 'mst_len_mean.pkl', 'wb') as f:
        pickle.dump(mean_length_list, f)
    f.close()

    with open(output_mst_len_path + 'mst_len_std.pkl', 'wb') as f:
        pickle.dump(mean_length_list, f)
    f.close()

    # Plot

    print('len list', mean_length_list)
    print('std', std_lenght_list)

    fig,ax = plt.subplots(figsize = (9,9))

    ax.plot(windows_list, mean_length_list, '-o')
    ax.fill_between(windows_list, mean_length_list - std_lenght_list, mean_length_list + std_lenght_list, color="orange", alpha=0.2, label="±1 std")
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.set_xlabel('Time', fontsize=20)
    ax.set_ylabel('MST length', fontsize=20)
    plt.show()

    fig.savefig(output_plot_path + 'window_tot_mean.png')
    print(output_plot_path)

    print('Time', end - start)