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
from min_spanning_tree_fun import *



# we compute it for:
# 1) time windows on total data
# 2) time windows by country
# 3) Framework Programme on total data
# 4) Framework Programme by country

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
parent_dir = cwd.parent.parent.parent

# data dir
data_dir = parent_dir / 'data new' #'Data'

# activity type : 'RES' or 'IND'
activity_type = 'RES'

# WHICH TYPE OF MST COMPUTE
mst_type = 'window tot'
# 'window tot'
# 'window country'
# 'FP tot'
# 'FP country'

# time window
time_window = 12 # months
step = 12 # months

# embeddings column -> total or reduced
embeddings_col = 'emb_list' # 'emb_list

# choose if total embeddings or umap or pca reduced embeddings
# umap
# pca
# no_red_emb
red_emb_type = 'no_red_emb'

# umap or PCA parameter -> dimensionality
components = 1024#768
#pca_components = 5


# choose how many points we need minimum to run MST
if embeddings_col == 'emb_list':
    points_threshold = 2
elif components <= 10:
    points_threshold = components
else:
    points_threshold = 2

# embeddings
emb = np.load('../embeddings_topics/description embeddings/bge_1024dim.npy')#embeddings_description.npy specter2_20dim_NORM.npy
if red_emb_type == 'umap':
    red_emb = np.load('embeddings_topics/description embeddings/red_emb_umap_' + str(components) + '.npy')
elif red_emb_type == 'pca':
    red_emb = np.load('embeddings_topics/PCA reduced embeddings/red_emb_' + str(components) + '.npy')


# output dir
if (mst_type == 'window tot') or (mst_type == 'window country'):
    if red_emb_type == 'umap':
        output_dir = 'min spanning tree/RES_IND knn norm' + str(time_window) + ' year_months step ' + str(step) + ' window/' + str(components) + ' umap/'
    elif red_emb_type == 'pca':
        output_dir = 'min spanning tree/RES_IND knn norm' + str(time_window) + ' year_months step ' + str(step) + ' window/' + str(components) + ' PCA/'
    elif red_emb_type == 'no_red_emb':
        output_dir = 'min spanning tree/' + activity_type + '/knn norm' + str(time_window) + ' year_months step ' + str(step) + ' window/tot emb/'

elif (mst_type == 'FP tot') or (mst_type == 'FP country'):
    if red_emb_type == 'umap':
        output_dir = 'min spanning tree CORRECT/FP/knn norm ' + str(components) + ' umap/'
    elif red_emb_type == 'pca':
        output_dir = 'min spanning tree CORRECT/FP/knn norm ' + str(components) + ' PCA/'
    elif red_emb_type == 'no_red_emb':
        output_dir = 'min spanning tree CORRECT/FP/knn norm tot emb/'


### PREPARE DATA

# 1) projects df

proj_dir = data_dir

list_beginning = [1984, 1987, 1990, 1994, 1998, 2002, 2007, 2014, 2021]
list_end = [1987, 1991, 1994, 1998, 2002, 2006, 2013, 2020, 2027]

list_df = []

#for i in range(1, 10):

df = pl.read_csv(data_dir / 'project_until_2025_no_nan_obj.csv')

df = df.with_columns(pl.Series(embeddings_col, list(emb)))

df_clean = df.filter(pl.col('startDate').is_not_null())

print(df_clean)

if activity_type == 'RES':
    df_res = pl.read_csv(data_dir / 'proj_res_H2020_HEU.csv')
    df_res = df_res.with_columns(pl.col("id").cast(pl.Utf8))
    df_clean = df_clean.join(df_res, on=['id', 'fp'])
elif activity_type == 'IND':
    df_ind = pl.read_csv(data_dir / 'proj_ind_H2020_HEU.csv')
    df_ind = df_ind.with_columns(pl.col("id").cast(pl.Utf8))
    df_clean = df_clean.join(df_ind, on=['id', 'fp'])

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
    print(df_fp)

# organizations dir
org_dir = data_dir / 'organizations'

# organizations df

org_df = pl.read_csv(data_dir / 'org_until_2025.csv', infer_schema_length=0, dtypes={"colname": pl.Utf8})

efta_df = pl.read_csv(data_dir / 'efta countries.csv')
efta_df = efta_df.with_columns(pl.col('country').str.to_lowercase())
efta_countries = efta_df['country'].to_list()


# 4) Merge proj + embeddings

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
    print(df_fp)



### COMPUTE MST

## 1) time windows on total data

if mst_type == 'window tot':

    # plot dir
    output_plot_dir = Path(output_dir + 'plot window tot_' + embeddings_col)
    output_plot_dir.mkdir(parents=True, exist_ok=True)
    output_plot_path = output_dir + 'plot window tot_' + embeddings_col + '/'


    # time windows
    window_size = time_window  # months
    step = step       # months

    # start and end date
    start_date = date(2014, 1, 1) #df["start_date"].min()
    end_date = date(2025, 12, 31) #df["end_date"].max()

    # initialization
    current_start = start_date
    windows_list = []
    windows_list = []
    results_graphs = []
    results_lengths = []
    length_list = []


    # create output country dir
    output_mst_len_dir = Path(output_dir + 'mst len window tot_' + embeddings_col)
    output_mst_len_dir.mkdir(parents=True, exist_ok=True)
    output_mst_len_path = output_dir + 'mst len window tot_' + embeddings_col + '/'
    print(output_mst_len_path)


    # create output windows time dir
    output_windows_dir = Path(output_dir + 'windows time tot_' + embeddings_col)
    output_windows_dir.mkdir(parents=True, exist_ok=True)
    output_windows_path = output_dir + 'windows time tot_' + embeddings_col + '/'


    start = time.time()

    count = 1

    while current_start <= end_date:

        print("# window: ", str(count) + "/" + str(86))

        current_end = current_start + relativedelta(months=window_size)
        
        window_df = proj_emb_df.filter(
            (pl.col("start_date") >= current_start) & 
            (pl.col("start_date") < current_end)
        )

        # extract points from embeddings
        points = [np.array(x) for x in window_df[embeddings_col].to_list()]
        points = np.array(points, dtype=float)

        print('# points in window:', len(points))

        if len(points) > points_threshold:

            dim = points.shape[1]

            chosen_k, comp_results = find_min_k_for_connectivity(points)

            # Build sparse graph (each node connected to k nearest neighbors)
            k = chosen_k
            knn_graph = kneighbors_graph(points, n_neighbors=k, mode='distance', include_self=False)
            knn_graph = knn_graph.maximum(knn_graph.T)
            #print(type(knn_graph))
            print('num nodes', knn_graph.shape[0])
            print('Num components:', connected_components(knn_graph))  
            
            # compute min spanning tree
            mst = minimum_spanning_tree(knn_graph)
            print('mst shape', mst.shape)
            print(f"Number of edges in MST: {mst.nnz}")
            print(f"Total MST length: {mst.sum()}")

            if mst != None:
                #length_list += [mst.sum() / (len(points)**((dim-1)/dim))]
                length_list += [mst.sum()]
                windows_list += [current_start] 
            
            #TODO COMMENTED
            # Slide by 6 months
            current_start = current_start + relativedelta(months=step)

        count += 1

    with open(output_windows_path + 'windows.pkl', 'wb') as f:
        pickle.dump(windows_list, f)
    f.close()

    with open(output_mst_len_path + 'mst_len.pkl', 'wb') as f:
        pickle.dump(length_list, f)
    f.close()

    end = time.time()

    # Plot

    fig,ax = plt.subplots(figsize = (9,9))

    ax.plot(windows_list, length_list, '-o')
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.set_xlabel('Time', fontsize=20)
    ax.set_ylabel('MST length', fontsize=20)
    plt.show()

    fig.savefig(output_plot_path + activity_type + '_window_tot.png')

    print('Time', end - start)


## 2) time windows by country

if mst_type == 'window country':

    # plot dir
    output_plot_dir = Path(output_dir + 'plot window country_' + embeddings_col)
    output_plot_dir.mkdir(parents=True, exist_ok=True)
    output_plot_path = output_dir + 'plot window country_' + embeddings_col + '/'


    window_size = window_size  # months
    step = time_window       # months

    start = time.time()

    for country in efta_countries:

        # create output country dir
        output_mst_dir = Path(output_dir + 'mst len window country_' + embeddings_col)
        output_mst_dir.mkdir(parents=True, exist_ok=True)
        output_mst_len_path = output_dir + 'mst len window country_' + embeddings_col + '/'

        # create output windows time dir
        output_windows_dir = Path(output_dir + 'windows time country_' + embeddings_col)
        output_windows_dir.mkdir(parents=True, exist_ok=True)
        output_windows_path = output_dir + 'windows time country_' + embeddings_col + '/'

        print(country)
        
        start_date = date(1983, 1, 1) #df["start_date"].min()
        end_date = date(2025, 12, 31) #df["end_date"].max()

        current_start = start_date
        windows_list = []
        results_graphs = []
        results_lengths = []
        length_list = []

        # projects + embeddings + organizations

        df_country = org_df.rename({'projectID': 'id'})
        df_country = df_country.filter(pl.col('country_code_ok') == country)
        
        df_country = df_country.with_columns(
            pl.col('fp').cast(pl.Int64).alias('fp_int')
        )
        df_country = df_country.drop('fp')
        df_country = df_country.rename({'fp_int': 'fp'})
        df_proj_emb_org = df_country.join(proj_emb_df, on=['id', 'fp'], how='left')
        
        count = 1

        while current_start <= end_date:
                
            print("# window: ", str(count) + "/" + str(86))

            current_end = current_start + relativedelta(months=window_size)
            
            window_df = df_proj_emb_org.filter(
                (pl.col("start_date") >= current_start) & 
                (pl.col("start_date") < current_end) &
                (pl.col(embeddings_col).is_not_null())
            )

            #window_df = window_df.unique(subset=[embeddings_col])

            # extract points from embeddings
            points = [np.array(x) for x in window_df[embeddings_col].to_list()]
            points = np.array(points, dtype=float)
            
            if len(points) > points_threshold:

                dim = points.shape[1]

                chosen_k, comp_results = find_min_k_for_connectivity(points)

                # Build sparse graph (each node connected to k nearest neighbors)
                k = chosen_k

                if k != None:
                    knn_graph = kneighbors_graph(points, n_neighbors=k, mode='distance', include_self=False)  
                    #print('Num components:', connected_components(knn_graph))  
                    
                    # compute min spanning tree
                    mst = minimum_spanning_tree(knn_graph)
                    print(f"Number of edges in MST: {mst.nnz}")
                    print(f"Total MST length: {mst.sum()}")

                    if mst != None:
                        length_list += [mst.sum() / (len(points)**((dim-1)/dim))]
                        windows_list += [current_start]

            count += 1
            
            # Slide by 6 months
            current_start = current_start + relativedelta(months=step)


        with open(output_windows_path + 'windows_' + country + '.pkl', 'wb') as f:
            pickle.dump(windows_list, f)
        f.close()

        with open(output_mst_len_path + 'mst_len_' + country + '.pkl', 'wb') as f:
            pickle.dump(length_list, f)
        f.close()

        # Plot
        print('Country:', country)
        fig,ax = plt.subplots(figsize = (9,9))

        ax.plot(windows_list, length_list, '-o')
        ax.tick_params(axis='both', which='major', labelsize=16)
        ax.set_xlabel('Time', fontsize=20)
        ax.set_ylabel('MST length', fontsize=20)
        plt.show()

        fig.savefig(output_plot_path + 'window_' + country + '.png')

    end = time.time()

    print('Time', end - start)



# 3) FP on total data

elif mst_type == 'FP tot':


    # plot dir
    output_plot_dir = Path(output_dir + 'plot FP tot_' + embeddings_col)
    output_plot_dir.mkdir(parents=True, exist_ok=True)
    output_plot_path = output_dir + 'plot FP tot_' + embeddings_col + '/'

    # create output country dir
    output_mst_len_dir = Path(output_dir + 'mst len FP tot_' + embeddings_col)
    output_mst_len_dir.mkdir(parents=True, exist_ok=True)
    output_mst_len_path = output_dir + 'mst len FP tot_' + embeddings_col + '/'


    fp_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    fp_name_list = ['FP1', 'FP2', 'FP3', 'FP4', 'FP5', 'FP6', 'FP7', 'H2020', 'Horizon \nEurope']

    length_list = []
    fp_plot_list = []

    count = 1

    start = time.time()

    for i in range(len(fp_list)):

        fp_df = proj_emb_df.filter(
            (pl.col("fp") == fp_list[i]) &
            (pl.col(embeddings_col).is_not_null())
        )

        print("FP: ", str(i+1))
        print("# projects: ", str(len(fp_df)))

        print('# projects no duplicates embeddings:', len(fp_df))
        print('# projects no duplicates proj id:', len(fp_df.unique(subset=['id'])))

        # extract points from embeddings
        points = [np.array(x) for x in fp_df[embeddings_col].to_list()]
        points = np.array(points, dtype=float)

        if len(points) > points_threshold:
            
            dim = points.shape[1]

            chosen_k, comp_results = find_min_k_for_connectivity(points)

            # Build sparse graph (each node connected to k nearest neighbors)
            k = chosen_k

            if k != None:
                knn_graph = kneighbors_graph(points, n_neighbors=k, mode='distance', include_self=False)  
                #print(type(knn_graph))
                #print('Num components:', connected_components(knn_graph))  
                
                # compute min spanning tree
                mst = minimum_spanning_tree(knn_graph)
                print(f"Number of edges in MST: {mst.nnz}")
                print(f"Total MST length: {mst.sum()}")

                if mst != None:
                    length_list += [mst.sum() / (len(points)**((dim-1)/dim))]
                    #length_list += [mst.sum()]
                    fp_plot_list += [fp_name_list[i]] # TODO ADDED THIS ROW

    
    with open(output_mst_len_path + 'mst_len.pkl', 'wb') as f:
        pickle.dump(length_list, f)
    f.close()
    
    end = time.time()

    # Plot

    fig,ax = plt.subplots(figsize = (9,9))

    ax.plot(fp_plot_list, length_list, '-o') # TODO CHANGED FROM fp_name_list TO fp_plot_list
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.set_xlabel('Time', fontsize=20)
    ax.set_ylabel('MST length', fontsize=20)
    plt.show()

    fig.savefig(output_plot_path + 'FP_tot.png')
    
    print('Time', end - start)


# 4) FP by country

elif mst_type == 'FP country':

    fp_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    fp_name_list = ['FP1', 'FP2', 'FP3', 'FP4', 'FP5', 'FP6', 'FP7', 'H2020', 'Horizon \nEurope']

    length_list = []

    num_proj_7 = 0
    num_proj_6 = 0

    start = time.time()

    for country in efta_countries:


        # plot dir
        output_plot_dir = Path(output_dir + 'plot FP country_' + embeddings_col)
        output_plot_dir.mkdir(parents=True, exist_ok=True)
        output_plot_path = output_dir + 'plot FP country_' + embeddings_col + '/'

        # create output country dir
        output_mst_dir = Path(output_dir + 'mst len FP country_' + embeddings_col)
        output_mst_dir.mkdir(parents=True, exist_ok=True)
        output_mst_len_path = output_dir + 'mst len FP country_' + embeddings_col + '/'

        print(country)
        
        length_list = []
        fp_plot_list = []

        count = 1

        for i in range(len(fp_list)):


            print('fp', i)
            
            org_df = pl.read_csv(org_dir + 'org_' + str(i+1) + '_updated_lat_lon.csv', infer_schema_length=0, dtypes={"colname": pl.Utf8})
            # projects + embeddings + organizations
            df_country = org_df.rename({'projectID': 'id'})
            df_country = df_country.filter(pl.col('country_code_ok') == country)
            df_country = df_country.with_columns(pl.lit(i+1).alias('fp'))

            df_proj_emb_org = df_country.join(proj_emb_df, on=['id', 'fp'], how='left')

            fp_df = df_proj_emb_org.filter(
                (pl.col("fp") == fp_list[i]) &
                (pl.col(embeddings_col).is_not_null())
            )

            print('FP:', fp_list[i])
            print('# projects:', len(fp_df))
            fp_df = fp_df.unique(subset=[embeddings_col]) #TODO ADDED THIS
            print('# projects no duplicates embeddings:', len(fp_df))
            print('# projects no duplicates proj id:', len(fp_df.unique(subset=['id'])))
            
        
            # extract points from embeddings
            points = [np.array(x) for x in fp_df[embeddings_col].to_list()]
            points = np.array(points, dtype=float)

            print('len point', len(points))
            
            if len(points) > points_threshold:

                dim = points.shape[1]

                chosen_k, comp_results = find_min_k_for_connectivity(points)

                # Build sparse graph (each node connected to k nearest neighbors)
                k = chosen_k

                if k != None:
                    knn_graph = kneighbors_graph(points, n_neighbors=k, mode='distance', include_self=False)  
                    #print('Num components:', connected_components(knn_graph))  
                    
                    # compute min spanning tree
                    mst = minimum_spanning_tree(knn_graph)
                    print(f"Number of edges in MST: {mst.nnz}")
                    print(f"Total MST length: {mst.sum()}")

                    if mst != None:
                        length_list += [mst.sum() / (len(points)**((dim-1)/dim))]
                        fp_plot_list += [fp_name_list[i]]


        with open(output_mst_len_path + 'mst_len_' + country + '.pkl', 'wb') as f:
            pickle.dump(length_list, f)
        f.close()

        # Plot
        print('Country:', country)
        fig,ax = plt.subplots(figsize = (9,9))

        ax.plot(fp_plot_list, length_list, '-o')
        ax.tick_params(axis='both', which='major', labelsize=16)
        ax.set_xlabel('Time', fontsize=20)
        ax.set_ylabel('MST length', fontsize=20)
        plt.show()

        fig.savefig(output_plot_path + 'FP_' + country + '.png')

    end = time.time()


    print('Time', end - start)