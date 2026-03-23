import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from transformers import AutoTokenizer 
#from umap import UMAP
from matplotlib import pyplot as plt
from huggingface_hub import login
import re
import json
import ast
import config_APIs
from org_match import *


# SET VARIABLES

# API KEY
HUGGINGFACE_TOKEN = config_APIs.HUGGINGFACE_LLAMA_TOKEN
login(token=HUGGINGFACE_TOKEN)

# ORGANIZATION MATCH INSTANCE -> for functions to compute organization matching
org_match = OrgMatch()


# Initialize the Llama model
#model_name = "meta-llama/Llama-3.2-3B-Instruct"  # Example for LLaMA 2, adjust as needed
model_name = "meta-llama/Meta-Llama-3.1-8B-Instruct"  # Example for LLaMA 2, adjust as needed
#model_name = "meta-llama/Meta-Llama-3.1-70B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
nlp = pipeline(model=model_name, 
               tokenizer=tokenizer,
                return_full_text=True, 
                task='text-generation',
                # we pass model parameters here too
                temperature=0.0,
                top_p=1,
                do_sample=False
)


def find_city_country(organization):
    '''
    Function to ask the LLM where an organization (or another thing) is located (which city)
    '''
    
    prompt = "In which city is " + organization + """ located? Return it as a single word """
    #prompt = f"In which city is {organization} located? Return it as a json with format \{"organization": str, "city": str\} and value the city?"
    #prompt = "In which city is " + organization + """ located? Return it as a json with format {"organization": str, "city": str}"""
    #In which city is {organization} located? Can you return a json with key {organization} and value the city?
    #Please answer the following question concisely and provide only the answer, without repeating the question or adding any explanation.\n Question: In which city is {organization} located?
    #In your reply can you just put a string containing the city and country without any other word of eplanation?
    
    # response
    response_0 = nlp(prompt, max_length=50, do_sample=False)[0]['generated_text']
    # clean response
    response = response_0.replace(prompt, '').strip()
        
    print(response)
    
    return response
    
    
def tot_find_city_country(file_city, output_file):
    '''
    Function to apply find_city_country to a set of organizations
    '''
    
    # Read the organizations from the CSV file
    df = pd.read_csv(file_city) #'org_to_llm.csv'

    # Apply the model query to each organization
    for i in range(len(df)):
        df.at[i, 'location'] = find_city_country(df.at[i, 'name'])

    # Save the updated DataFrame with city and country to a new CSV
    df.to_csv(output_file, index=False) #'organizations_with_locations_3.2_0.csv'

    print("Locations saved to " + output_file)


#TODO STILL TO FINISH TO IMPLEMENT
def tot_match_organization(file_input, city_col, org_col, n): # n = size of sublists to send to openai -> NB: n must be multiple of 2 otherwise we break pairs that need to be compared
    '''
    Extract organizations names that represent the same entity
    '''

    df_input = pd.read_csv(file_input)
    print(df_input)
    
    # find same organizations
    for i in range(len(df_input)):
        
        # take city and list of organizations
        city_org = df_input.at[i, city_col]
        list_org = ast.literal_eval(df_input.at[i, org_col])
        
        # compute all the possible combinations and group them into lists to have each pair in at least one of them -> reduced_ll_org is a list of lists
        reduced_ll_org = org_match.extract_tot_pairs(list_org, n)
        
        #message = list_org + " this is a list of organizations located in " + city + ", can you tell me which of them represent the same organization? Return the output as a list of lists, where we have in each list the organizations that match, return the ones that have no match in single lists. Also, return only the list without any other additional sentence"
        #message = list_org + " this is a list of organizations located in " + city + ", can you tell me which of them represent the same organization? Return the output as a dictionary with key a name indicating the organization and value the list of the organizations matching that one, return a different key for each of the ones that have no match. Also, return only the dictionary without any other additional sentence"


        for l_org in reduced_ll_org: # l_org is a list of organizations
                        
            #response_0 = None
            
            #prompt = str(list(l_org)) + " this is a list of organizations located in " + city_org + ", can you tell me which of them represent the same organization? Return the output as a dictionary with key a name indicating the organization and value the list of the organizations matching that one, for the ones that have no match return a key 'random' with them as value. Also, return only the dictionary without any other additional sentence"
            prompt = str(list(l_org)[0]) + " is this a list of organizations located in " + city_org + "?"#, can you tell me which of them represent the same organization? Return the output as a dictionary with key a name indicating the organization and value the list of the organizations matching that one, for the ones that have no match return a key 'random' with them as value. Also, return only the dictionary without any other additional sentence"
            
            #prompt = "In which country is " + city_org + "? Return city, country code in ISO2 with no additional words. If you don't know the answer return nan, nan"
            print('ciao', prompt)
            try:
                response_0 = nlp(prompt, max_length=4000, do_sample=False)[0]['generated_text']#max_length=500, 
            except:
                print('Error at line ' + str(i))
            
            print(response_0)
            
            '''if response_0 is not None:
                response = response_0.replace(prompt, '').strip()
                
                # extract dictionary from text of openai output
                d_llama = org_match.extract_dictionary(response)
                if d_llama is not None:
                    if 'random' in d_llama:
                        print('random d', d_llama)
                        if d_llama['random'] is None:
                            d_llama.pop('random')
                        else:
                            for el in d_llama['random']:
                                d_llama['random_' + el] = [el]
                            d_llama.pop('random')            
                
                # from dictionary to list of lists -> the values of the dictionary become the sublists in this list
                d_llama = org_match.dict_to_list(d_llama)
                print('list of lists', d_llama)
                
                # l_tot = [['unimi', '...', '...'], ['...', '...', '...'], ...] -> for each l_org , we extract the org that match, so we obtain d_llama [['...', '...', '...'], ['...', '...', '...'], ...] and we add its elements to l_tot
                l_tot += d_llama
                print('l tot', l_tot)
            
        
        # find same organizations by combining the results from different batches
        org_match_tot = org_match.extract_org_match(l_tot)
        
        # save the results
        with open(city_org + '_1.json', 'w') as json_file:
            json.dump(org_match_tot, json_file, indent=4)'''






























'''print("Cities added and saved to 'organizations_with_cities.csv'")

# 1. Load a pretrained Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# dataset play
df = pd.read_csv('data/H2020/2020/cordis-h2020projects.csv', sep=';').head(10)'''
#df = pd.read_csv('topic_trial.csv')

# The sentences to encode
'''sentences = [
"The weather is lovely today.",
"It's so sunny outside!",
"He drove to the stadium.",
]'''
'''sentences = df.objective.tolist()

# 2. Calculate embeddings by calling model.encode()
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# 3. Calculate the embedding similarities
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.6660, 0.1046],
# [0.6660, 1.0000, 0.1411],
# [0.1046, 0.1411, 1.0000]])

# reduce embeddings for visualization purposes
umap_model = UMAP(n_neighbors=15, n_components=2, min_dist=0.0, metric='cosine', random_state=42)
reduced_embeddings = UMAP(n_neighbors=15, n_components=2, min_dist=0.0, metric='cosine', random_state=42).fit_transform(embeddings)

print(reduced_embeddings)
print(reduced_embeddings.shape)


from sentence_transformers import SentenceTransformer

# Load SBERT model (paraphrase-mpnet-base-v2 is one of the best for similarity)
model = SentenceTransformer('sentence-transformers/paraphrase-mpnet-base-v2')

# Example list of documents (300-word texts)
documents = ["This is the first document...", "This is the second document...", "More documents here..."]

# Generate embeddings for each document
embeddings = model.encode(documents)




# Plotting the embeddings
plt.figure(figsize=(8, 6))
plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], color='blue', s=100)
for i, (x, y) in enumerate(reduced_embeddings):
    plt.text(x + 0.01, y + 0.01, f"Emb_{i+1}", fontsize=12)

    plt.title("2D Projection of Embeddings using UMAP")
    plt.xlabel("UMAP Component 1")
    plt.ylabel("UMAP Component 2")
    plt.grid(True)
    plt.show()

df = pd.DataFrame(reduced_embeddings)
df.to_csv('stuff/prova_embeddings.csv')'''