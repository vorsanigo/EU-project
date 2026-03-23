from openai import OpenAI
import pandas as pd
import json
import config_APIs
from org_match import *


# SET VARIABLES
#file = 'grouped_org_filtered.csv'
# INPUT FILE
file = 'jonkoping.csv'
# API KEY - ORGANIZATION NAME FOR OPENAI
API_KEY = config_APIs.OPENAI_KEY
ORGANIZATION = config_APIs.OPENAI_ORGANIZATION
# ORGANIZATION MATCH INSTANCE -> for functions to compute organization matching
org_match = OrgMatch()


# generate text
df_input = pd.read_csv(file)#.head(5)
df_output = pd.DataFrame()

    
client = OpenAI(
    organization=ORGANIZATION,
    #project='Default project',
    api_key=API_KEY,
)


# find city of organization   

'''for i in range(len(df_input)):
    
    organization = df_input.at[i, 'name']
    
    message = "In which city and country is" + organization + "? Return city, country code in ISO2 with no additional words. If you don't know the answer return nan, nan"
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": message
            }
        ]
    )

    answer = None
    city = None
    country = None
    try:
        answer = completion.choices[0].message.content
    except:
        print('Error at line ' + str(i))
    try:
        split_answer = answer.split(',')
    except:
        print('Error at line ' + str(i))
    try:
        city = split_answer[0]
    except:
        print('Error at line ' + str(i))
    try:
        country = split_answer[1]
    except:
        print('Error at line ' + str(i))
    df_output = df_output._append({'organization': organization, 'city': city, 'country': country}, ignore_index=True)
    
    
df_output.to_csv('city_openai.csv', index=False)'''




def tot_match_organization(df_input, city_col, org_col, n): # n = size of sublists to send to openai -> NB: n must be multiple of 2 otherwise we break pairs that need to be compared

    # find same organizations
    for i in range(len(df_input)):
        
        # take city and list of organizations
        city_org = df_input.at[i, city_col]
        list_org = ast.literal_eval(df_input.at[i, org_col])
        
        reduced_ll_org = org_match.extract_tot_pairs(list_org, n)
        
        #message = list_org + " this is a list of organizations located in " + city + ", can you tell me which of them represent the same organization? Return the output as a list of lists, where we have in each list the organizations that match, return the ones that have no match in single lists. Also, return only the list without any other additional sentence"
        #message = list_org + " this is a list of organizations located in " + city + ", can you tell me which of them represent the same organization? Return the output as a dictionary with key a name indicating the organization and value the list of the organizations matching that one, return a different key for each of the ones that have no match. Also, return only the dictionary without any other additional sentence"

        # list of results
        l_tot = []
        
        for l_org in reduced_ll_org:
            
            '''print('l org', l_org)'''
            
            message = str(l_org) + " this is a list of organizations located in " + city_org + ", can you tell me which of them represent the same organization? Return the output as a dictionary with key a name indicating the organization and value the list of the organizations matching that one, for the ones that have no match return a key 'random' with them as value. Also, return only the dictionary without any other additional sentence"
        
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                max_tokens=8384
            )
            
            answer = None
            
            try:
                answer = completion.choices[0].message.content
            except:
                print('Error at line ' + str(i))
                
                

            # extract dictionary from text of openai output
            d_openai = org_match.extract_dictionary(answer)
            if d_openai is not None:
                if 'random' in d_openai:
                    print('random d', d_openai)
                    '''if len(d_openai['random']) == 0:
                        d_openai.pop('random')'''
                    if d_openai['random'] is None:
                        d_openai.pop('random')
                    else:
                        for el in d_openai['random']:
                            d_openai['random_' + el] = [el]
                        d_openai.pop('random')
            print('random next', d_openai)
            
            
            # from dictionary to list of lists -> the values of the dictionary become the sublists in this list
            l_openai = org_match.dict_to_list(d_openai)
            print('list of lists', l_openai)
            
            # l_tot = [['unimi', '...', '...'], ['...', '...', '...'], ...] -> for each l_org , we extract the org that match, so we obtain l_openai [['...', '...', '...'], ['...', '...', '...'], ...] and we add its elements to l_tot
            l_tot += l_openai
            print('l tot', l_tot)
            
        
        # find same organizations by combining the results from different batches
        org_match_tot = org_match.extract_org_match(l_tot)
        
        # save the results
        with open(city_org + '.json', 'w') as json_file:
            json.dump(org_match_tot, json_file, indent=4)


#TODO add controls
# if we get dictionary from extract_dictionary or we get none or empty thing
# if 'random' is a list
# line 94 -> improve results