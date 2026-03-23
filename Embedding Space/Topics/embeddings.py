import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from umap import UMAP
from matplotlib import pyplot as plt
import argparse
from pathlib import Path

import torch
torch.cuda.empty_cache()


# set directory
cwd = Path.cwd()
parent_dir = cwd.parent.parent

#TODO SET PATH DATASET


# arguments parser
parser = argparse.ArgumentParser(description='Embeddings parameters')

# inputs
parser.add_argument('-documents_to_clean',
                    type=str,
                    default='../Data/projects_until_2025.csv',
                    help='Path of document to use to extract embeddings')
# outputs
parser.add_argument('-output_emb_df',
                    type=str,
                    default='embeddings_topics/description embeddings/embeddings_info_description.csv')
parser.add_argument('-output_emb_plot',
                    type=str,
                    default='embeddings_topics/description embeddings/embeddings_description.png')
parser.add_argument('-output_emb_npy',
                    type=str,
                    default='embeddings_topics/description embeddings/embeddings_description.npy')
parser.add_argument('-output_red_emb_npy',
                    type=str,
                    default='embeddings_topics/description embeddings/reduced_embeddings_description.npy')
# columns
parser.add_argument('-description_column',
                    type=str,
                    default='objective',
                    help='Column of descriptions')
parser.add_argument('-title_column',
                    type=str,
                    default='title',
                    help='Column of descriptions')
parser.add_argument('-fp_column',
                    type=str,
                    default='fp',
                    help='Column of framework programme')
parser.add_argument('-proj_id_column',
                    type=str,
                    default='id',
                    help='Column on which we do topic modeling')
# embedding model
parser.add_argument('-model',
                    type=str,
                    default='BAAI/bge-m3',
                    help='Model to use for embeddings') #paraphrase-mpnet-base-v2

args = parser.parse_args()


# dataset
file = args.documents_to_clean

# output
embeddings_df = args.output_emb_df
embeddings_plot = args.output_emb_plot
embeddings_np = args.output_emb_npy
reduced_embeddings_np = args.output_red_emb_npy

# variables
topic_column = args.topic_column
fp_column = args.fp_column
proj_id_column = args.proj_id_column

# model
model_emb = args.model

# Load a pretrained Sentence Transformer model
#model = SentenceTransformer("all-MiniLM-L6-v2") # model 1: faster, good embedding quality but not as fine-grained, for real-time, large-scale applications, for real-time/large-scale applications, short to medium sentences
model = SentenceTransformer(model_emb) # model 2: slower, high-quality of embedding, high-accuracy semantic tasks, paraphrase detection and text similarity, short to longer and complex sentences

print('Model loaded')


# dataset play
df = pd.read_csv(file)


# using project description
# remove rows with description = nan
df = df[~df[topic_column].isna()]
df = df.reset_index()


# framework programmes
fp = df[fp_column].tolist()

# IDs of projects
ids = df[proj_id_column].tolist()



# The sentences to encode -> 'objective' column
sentences = df[topic_column].tolist()

print('Data ready')


print('Starting encoding embeddings')
# Calculate embeddings by calling model.encode()
embeddings = model.encode(sentences)
print('Extracted embeddings')
print(embeddings.shape)



print('Starting reducing embeddings')
# reduce embeddings for visualization purposes
umap_model = UMAP(n_neighbors=15, n_components=2, min_dist=0.0, metric='cosine', random_state=42)
reduced_embeddings = UMAP(n_neighbors=15, n_components=2, min_dist=0.0, metric='cosine', random_state=42).fit_transform(embeddings)
print('Reduced embedding')


# df embeddings
df_embeddings = pd.DataFrame()
df_embeddings[fp_column] = fp
df_embeddings[proj_id_column] = ids
df_embeddings['embeddings'] = list(np.array(embeddings))
df_embeddings['reduced embeddings'] = list(np.array(reduced_embeddings))
df_embeddings.to_csv(embeddings_df, index=False)


# Plotting the embeddings
plt.figure(figsize=(8, 6))
plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], color='blue', s=10, alpha=0.1)

#plt.title("2D Projection of Embeddings using UMAP")
plt.xlabel("UMAP Component 1")
plt.ylabel("UMAP Component 2")
plt.grid(False)
plt.show()
plt.savefig(embeddings_plot)


np.save(embeddings_np, embeddings)
np.save(reduced_embeddings_np, reduced_embeddings)

print('Saved embeddings')
