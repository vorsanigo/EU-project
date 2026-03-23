from itertools import permutations
import re
import ast
import re


class OrgMatch():
    '''
    Nominatim geocoder based on OpenStreetMap
    Attributes:
        - server_url
        - address_details
        - format: results format
        - maxRows: max number of results
        - lang: results language
        - sleep_time: sleep time for Nominatim requests
    '''

    '''def __init__(self, server_url = 'https://nominatim.openstreetmap.org/', address_details = '?addressdetails=1&q=',
                 format = 'json', maxRows = 1, lang = 'en', sleep_time = 0.2):

        self.server_url = server_url
        self.address_details = address_details
        self.format = format
        self.maxRows = maxRows
        self.lang = lang
        self.sleep_time = sleep_time'''


    # functions to create input to send to openai

    def all_combinations(self, el_list, combination_num):
        '''
        Given a list, extract all the permutaions of n = combination_num elements
        '''
        
        combinations = list(permutations(el_list, combination_num))

        return combinations


    def divide_list(self, lst, n):
        '''
        Given a list, divide it into lists of n elements each, if len(list) not divisible by n, put the remaining elements in the last sublist
        '''
        
        return [lst[i:i + n] for i in range(0, len(lst), n)]


    def extract_tot_pairs(self, el_list, n):
        '''
        Given a list of elements, compute all their possible combinations, group them so that each pair appears at least in one of the tuples, remove duplicated organizations names from the tuples, merge tuples with 
        number of elements < of a certain number to reduce number of batches (tuples)
        '''
        
        # extract all the possible pairs from list of organizations
        list_of_tuples = self.all_combinations(el_list, 2)
        flattened_org = [item for t in list_of_tuples for item in t]
        
        # list of lists -> divide the flattened list in a list of lists of length = n -> [['milano uni', 'uni milan', 'polimi'], ['uni mil', 'unimib', 'poli'], ...] -> here: n = 3
        ll_org = self.divide_list(flattened_org, n)
        
        # from lists get sets to remove duplicates within the same list -> [{'milano uni', 'uni milan', 'polimi'}, {'uni mil', 'unimib', 'poli'}, ...]
        for i in range(len(ll_org)):
            ll_org[i] = set(ll_org[i])
        
        # merge the ones that have len < n such that if merged their size remains <= n
        reduced_ll_org = self.reduce_num_sets(ll_org, n)
        
        return reduced_ll_org
    
    
    # functions to work on the output of openai
    
    
    def extract_dictionary(self, text):
        '''
        Given a piece of text, extract the dictionary from it
        '''
        
        # Use a regular expression to find the part of the text that looks like a dictionary
        pattern = r"\{[^{}]*\}"
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                # Safely evaluate the potential dictionary
                result = ast.literal_eval(match)
                if isinstance(result, dict) and all(isinstance(v, list) for v in result.values()):
                    '''print('dictionary')'''
                    return result
            except Exception:
                continue
        return None


    def dict_to_list(self, d):
        '''
        Given a dictionary, it returns the list of the values (in our case values are other lists)
        '''
        
        l = []
        
        for key, value in d.items():
            l += [value]
        
        return l


    def extract_org_match(self, list_of_sets):
        '''
        Given a list of sets of organizations (the ones in the same list represent the same organization), find same organizations across the lists
        '''
        
        d = {}
        
        # put all the sublists in a dictionary with their key
        for i in range(len(list_of_sets)):
            d[str(i)] = set(list_of_sets[i])

        '''print('d initial', d)'''
            
        keys = list(d.keys())
        '''print(keys)'''
        
        for i in range(len(keys)):
            '''print(keys[i])'''
        # iterate over the list of lists (turned into sets), do intersection, if it not empty, do the union and update the values of the keys with the union
        for i in range(len(keys) - 1):
            for y in range(i+1, len(keys)):
                if i < len(keys)-1 and y < len(keys):
                    '''print('i', i)
                    print('y', y)'''
                    key = keys[i]
                    next_key = keys[y]
                    '''print('key', key)
                    print('next_key', next_key)'''
                    set1 = d[key]
                    set2 = d[next_key]
                    '''
                    print('d_key', d[key])
                    print('d_next_key', d[next_key])'''
                    # if the intersection of the two sets is not empty: set the value of the first key as the unoion of the two sets, remove the second key-value from the dictionary (since it is already in the union), remove the second key from 
                    if len(set1.intersection(set2)) != 0:
                        d[key] = set1.union(set2)
                        removed_value = d.pop(next_key)
                        keys.remove(next_key)
                    '''print(keys)
                    print(d)'''
        
        '''print('d final', d)'''
        
        for key, value in d.items():
            d[key] = list(value)
            
        '''print('d final list', d)'''
                    
        return d
    
    
    def reduce_num_sets(self, list_of_sets, set_size):

        # merge the ones that have len < n such that if merged their size remains <= n
        i = 0
        y = 1
        l = len(list_of_sets)
        
        while i < l-1:
            while y < l:
                union = list_of_sets[i].union(list_of_sets[y])
                '''print(i)
                print(y)'''
                if len(union) <= set_size:
                    indeces_to_remove = [i, y]
                    for index in sorted(indeces_to_remove, reverse=True):
                        del list_of_sets[index]
                    list_of_sets += [union]
                    i = -1
                    y = 1
                    l = len(list_of_sets)
                    '''print('list break', list_of_sets)'''
                    break
                else:
                    y += 1
                '''print('list', list_of_sets)'''
            i += 1
            
        '''print(list_of_sets)'''
        
        return list_of_sets

    '''def text_to_dict_match(self, text, output):
        
        d_openai = self.extract_dictionary(text)
        l_openai = self.dict_to_list(d_openai)
        org_match = self.extract_org_match(l_openai)
        
        print(type(org_match))
        
        print('res dict', org_match)
        
        with open('prova.json', 'w') as json_file:
            json.dump(org_match, json_file, indent=4)
        
        return org_match'''




'''text = ciciciic
{
    'Almi Företagspartner Jönköping AB': [
        'almi f�retagspartner j�nk�ping ab', 
        'almi företagspartner jönköping ab', 
        'almi foretagspartner jonkoping ab'
    ],
    'Svenska Gjuteriföreningen': [
        'svenska gj�terif�reningen', 
        'svenska gjuteriforeningen'
    ],
    'Länsteknikcentrum i Jönköpings Län AB': [
        'länsteknikcentrum i jönköpings län ab', 
        'lansteknikcentrum i jonkopings lan ab'
    ],
    'Euro Info Centre Jönköping Iän AB': [
        'euro info centre jönköping iän ab', 
        'euro info centre jönköpings iän ab'
    ],
    'Högskolan för Lärande och Kommunikation i Jönköping - HLK School of Education and Communication': [
        'hogskolan for larande och kommunikation i jonkoping - hlk school of education and communication'
    ],
    'Internationella Handelshögskolan i Jönköping': [
        'internationella handelshogskolan ijonkoping ab*ihh'
}

d = extract_dictionary_with_lists(text)


print(d)'''







'''l = [['milan uni', 'unimi'], ['univ of milan', 'unimi'], ['polimi'], ['agrate bz shop', 'shop ed', 'ddd'], ['polimi', 'politecnico milano'], ['unimi', 'univ mil']]
#d = extract_org_match(l)
#print('ddd', d)'''

'''d = {'0': {'milan uni', 'unimi', 'univ of milan', 'univ mil'}, '2': {'politecnico milano', 'polimi'}, '3': {'ddd', 'agrate bz shop', 'shop ed'}}
l = dict_to_list(d)
print(l)'''
'''
l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
o = OrgMatch()
print(o.divide_list(l, 3))'''

'''l = ['milan uni', 'unimi', 'univ of milan', 'polimi', 'agrate bz shop', 'shop ed', 'ddd']


org = OrgMatch()

co = org.all_combinations(l, 2)

print(co)'''


'''d = {'a': [1,2,3], 'd': []}
if len(d['d']) == 0:
    print('ciao')'''
        
    










