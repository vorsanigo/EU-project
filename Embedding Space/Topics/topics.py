import pandas as pd
#from sentence_transformers import SentenceTransformer
#from umap import UMAP
from matplotlib import pyplot as plt
import numpy as np
#import torch
import ast


import pandas as pd
import pickle
from nltk.corpus import stopwords
import nltk
from bertopic import BERTopic
from huggingface_hub import login
from sklearn.feature_extraction.text import CountVectorizer
import gensim.corpora as corpora
from gensim.models.coherencemodel import CoherenceModel
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from torch import cuda
from torch import bfloat16
import transformers
from umap import UMAP
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance, TextGeneration
import argparse
import json
import time
from transformers import AutoModel, AutoTokenizer

import torch
torch.cuda.empty_cache()

import config_topics


# INITIALIZATION

# API KEY
HUGGINGFACE_TOKEN = config_topics.HUGGINGFACE_TOKEN
login(token=HUGGINGFACE_TOKEN)


# arguments parser
parser = argparse.ArgumentParser(description='Topic modeling parameters')
# files
parser.add_argument('-df_emb',
                    type=str,
                    default='../embeddings_topics/description embeddings/bge_1024dim_info.csv',
                    help='Path to the df with embeddings info')
parser.add_argument('-npy_emb',
                    type=str,
                    default='../embeddings_topics/description embeddings/bge_1024dim.npy',
                    help='Path to the df with embeddings info')
parser.add_argument('-doc_df',
                    type=str,
                    default='../../Data/project_until_2025_no_nan_obj.csv',
                    help='Path to the df with embeddings info')
parser.add_argument('-doc_json',
                    type=str,
                    default='../../Data/corpus.json',
                    help='Path to the df with embeddings info')
parser.add_argument('-output_dir',
                    type=str,
                    default='../embeddings_topics/description_topics/',
                    help='Output directory for topics')
# columns names
parser.add_argument('-description_column',
                    type=str,
                    default='objective',
                    help='Column of projects descriptions')
parser.add_argument('-fp_column',
                    type=str,
                    default='fp',
                    help='Column of framework programme')
parser.add_argument('-title_column',
                    type=str,
                    default='title',
                    help='Column of projects title')
parser.add_argument('-proj_id_column',
                    type=str,
                    default='id',
                    help='Column on which we do topic modeling')
# topic modeling parameters
parser.add_argument('-umap_neighbours',
                    type=int,
                    default=15,
                    help='UMAP number of neighbours')
parser.add_argument('-umap_components',
                    type=int,
                    default=2,
                    help='UMAP components')
parser.add_argument('-hdbscan_param',
                    type=int,
                    default=100,
                    help='HDBSCAN parameter')
parser.add_argument('-cluster_selection_epsilon',
                    type=float,
                    default=0.07,
                    help='HDBSCAN parameter for epsilon')
parser.add_argument('-top_n_words',
                    type=int,
                    default=15,
                    help='top n words for representation of the topic')
parser.add_argument('-nr_topics',
                    type=int,
                    default=-1,#10
                    help='Number of topics we want')
parser.add_argument('-model',
                    type=str,
                    default='BAAI/bge-m3',
                    help='Model used for embeddings')   #sentence-transformers/paraphrase-mpnet-base-v2
args = parser.parse_args()



nltk.download('stopwords')


# inputs
# df embeddings info
file_embeddings_info = args.df_emb
# file npy embeddings
file_embeddings = args.npy_emb
# df projects documents
file_documents = args.doc_df
# json projects documents
file_documents_json = args.doc_json

# output dir
output_dir = args.output_dir

# variables
fp_column = args.fp_column
proj_id_column = args.proj_id_column
title_column = args.title_column
description_column = args.description_column

# umap and hdbscan parameters
umap_neighbours = args.umap_neighbours
umap_components = args.umap_components
hdbscan_param = args.hdbscan_param
cluster_epsilon = args.cluster_selection_epsilon

# top_n_words
top_n_words = args.top_n_words

# embeddings model
model_emb = args.model

# outputs
df_topic_document = output_dir + 'umap_' + str(umap_components) + '_hdbscan_' + str(hdbscan_param) + '/topics_project_umap_' + str(umap_components) + '_hdbscan_' + str(hdbscan_param) + '.csv'
df_topic_info = output_dir + 'umap_' + str(umap_components) + '_hdbscan_' + str(hdbscan_param) + '/info_topic_umap_' + str(umap_components) + 'hdbscan_' + str(hdbscan_param) + '.csv'
topic_model_path = output_dir + 'umap_' + str(umap_components) + '_hdbscan_' + str(hdbscan_param) + '/topic_model_umap_' + str(umap_components) + '_hdbscan_' + str(hdbscan_param)
hierarchy_path = output_dir + 'umap_' + str(umap_components) + '_hdbscan_' + str(hdbscan_param) + '/'
red_embeddings_path = output_dir + 'umap_' + str(umap_components) + '_hdbscan_' + str(hdbscan_param) + 'red_emb_umap_' + str(umap_components) + '.npy'
hierarchical_topics_path = output_dir + 'umap_' + str(umap_components) + '_hdbscan_' + str(hdbscan_param) + '/hierarchical_topics.csv'
probabilities_path = output_dir + 'umap_' + str(umap_components) + '_hdbscan_' + str(hdbscan_param) + '/probabilities.npy'


# LOAD EMBEDDINGS, DOCUMENTS AND DEFINE OUTPUT DF

# df embeddings
print('df embeddings')
df_embeddings = pd.read_csv(file_embeddings_info)#.head(300)
print('len embeddings', len(df_embeddings))
print('Columns of embeddings df', df_embeddings.columns)
print('Length embeddings:', len(df_embeddings))
# df projects
print('df projects')
df_documents = pd.read_csv(file_documents)#.head(300)
#df_documents = df_documents[~df_documents[topic_column].isna()]
print('Columns of documents df', df_documents.columns)
print('Length documents:', len(df_documents))

# json projects
corpus = pd.read_json(file_documents_json, orient='records')
corpus['text'] = corpus['title'] + ' ' + corpus['objective']
documents_list = corpus['text'].to_list()

# embedings
embeddings_0 = np.load(file_embeddings)
embeddings = embeddings_0

print(len(df_embeddings))
print(len(df_documents))
print(len(embeddings))

# remove nan -> no need since there are no nan
#df_topic1 = df_topic[~df_topic[documents_column].isna()]

# set variables
# list of documents
#print(df_documents.columns)
#documents_list = df_documents[topic_column].tolist()
# create df eith documents and related topic number
# set columns names
topics_df_new = pd.DataFrame()
topics_df_new[fp_column] = df_documents[fp_column]
topics_df_new[proj_id_column] = df_documents[proj_id_column]
topics_df_new[title_column] = df_documents[title_column]
topics_df_new['text'] = corpus['text']


# remove stopwords
lang_stopwords = 'english'
stopwords = stopwords.words(lang_stopwords)
# use CountVectorizer to remove stopwords
vectorizer_model = CountVectorizer(stop_words=stopwords)



# UMAP AND HDBSCAN

# set submodels
# umap
umap_model = UMAP(n_neighbors=umap_neighbours, n_components=umap_components, min_dist=0.0, metric='cosine', random_state=42)
# hdbscan
hdbscan_model = HDBSCAN(min_cluster_size=hdbscan_param, metric='euclidean', cluster_selection_method='eom', prediction_data=True) #cluster_selection_epsilon=cluster_epsilon, 


topic_model = BERTopic(

  # Sub-models
  #embedding_model=embedding_model,
  vectorizer_model=vectorizer_model,
  umap_model=umap_model,
  hdbscan_model=hdbscan_model,
  #representation_model=representation_model,

  # Hyperparameters
  top_n_words=top_n_words,
  verbose=True,
  #nr_topics = n

  calculate_probabilities=True
  
)

print('Starting topic modeling')

start = time.time()

# Train model
topics, probs = topic_model.fit_transform(documents_list, embeddings)
end = time.time()
print('PROBS')
print(probs)
print(f'Time: {end - start}')


print('Topic modeling computed')


'''print('Compute probabilities')
start = time.time()
# extract dominants probabilities
dominant_probs = probs.max(axis=1)
end = time.time()'''




# extract reduced embeddings
try:
    reduced_embeddings = topic_model.umap_model.embedding_
except Exception as e:
    print(f"First method does not work: {e}")

    try:
        reduced_embeddings = topic_model._embedding_model
    except Exception as e:
        print(f"Second method does not work: {e}")

        try:
            embeddings = topic_model._extract_embeddings(documents_list, verbose=True)
            reduced_embeddings = topic_model.umap_model.transform(embeddings)
        
        except Exception as e:
            print(f"Third method does not work: {e}")

try:
    np.save(red_embeddings_path, reduced_embeddings)
except Exception as e:
    print(f"No embeddings: {e}")



# add topics to df & their probabilities (of the most probable, namely topics)
topics_df_new['topic_num'] = topics
#topics_df_new['probability'] = dominant_probs #dominants_probs 


print('Counting outliers')

# Count outliers
outliers_count = topics.count(-1)

# Reduce outliers
if outliers_count > 0:
    # trivial strategy
    new_topics = topic_model.reduce_outliers(documents_list, topics)
    # probabilities
    topics_prob = topic_model.reduce_outliers(documents_list, topics, probabilities=probs, strategy="probabilities")
    # topic distributions
    topics_distr = topic_model.reduce_outliers(documents_list, topics, strategy="distributions")
    # c-TF-IDF
    topics_c_tf_idf = topic_model.reduce_outliers(documents_list, topics, strategy="c-tf-idf")
    # embeddings
    #topics_embeddings = topic_model.reduce_outliers(documents_list, topics, strategy="embeddings")
    
    # add topics to df
    topics_df_new['topic_num_forced'] = new_topics
    topics_df_new['topic_num_prob'] = topics_prob
    topics_df_new['topic_num_distr'] = topics_distr
    topics_df_new['topic_num_c_tf_idf'] = topics_c_tf_idf
    #topics_df_new['topic_num_embeddings'] = topics_embeddings

print('Outliers computed')


print('Hierarchical topic modeling')

#Hierarchical topics
hierarchical_topics = topic_model.hierarchical_topics(documents_list)
# Visualize hierarchical topics
topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
tree = topic_model.get_topic_tree(hierarchical_topics)
# create figure hierarchy
fig_hierarchy = topic_model.visualize_hierarchy()

print(tree)
print('Hierarchical topics computed')


# SAVE STUFF

print('Saving')

# save topics df
topics_df_new.to_csv(df_topic_document, index=False)

# get topics info
info_df = topic_model.get_topic_info()
info_df.to_csv(df_topic_info, index=False)

# save all the probabilities
np.save(probabilities_path, probs)


# save topic model
topic_model.save(topic_model_path + '_pickle', serialization='pickle')
topic_model.save(topic_model_path + 'pytorch', serialization='pytorch', save_ctfidf=True, save_embedding_model=model_emb)
topic_model.save(topic_model_path + 'safetensor', serialization='safetensors', save_ctfidf=True, save_embedding_model=model_emb) # sentence-tranformers/paraphrase-mpnet-base-v2

# save hierarchical topics into csv
hierarchical_topics.to_csv(hierarchical_topics_path)
# save hierarchy
fig_hierarchy.write_html(hierarchy_path + 'hierarchy.html')


# Visualization
# topics
'''fig_topics = topic_model.visualize_topics()
fig_topics.write_image(plot_path + 'topics.png')'''
# hierarchy
#fig_hierarchy.write_image(plot_path + 'hierarchy.png')
# topic terms
'''fig_terms = topic_model.visualize_barchart()
fig_terms.write_image(plot_path + 'topic_terms.png')
# topic similarity
fig_similarity = topic_model.visualize_heatmap()
fig_similarity.write_image(plot_path + 'topic_similarity.png')'''


print(topic_model.get_topic_info())
print(topic_model.topic_representations_)
print(topic_model.vectorizer_model)
print(topic_model.embedding_model)


print('Done')