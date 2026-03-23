import pandas as pd
import csv
import numpy as np
import ast

#print(sys.executable)


def write_dict_to_csv(dictionary, filename, columns):
    '''
    Write from dictionary to csv
    '''
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        for key, value in dictionary.items():
            writer.writerow([key, value])



def write_dict_to_df(dictionary, columns):
    '''
    From dictionary to dataframe
    '''

    df = pd.DataFrame(columns=columns)
    for key, value in dictionary.items():
        df = df._append({columns[0]: key, columns[1]: value}, ignore_index=True)

    return df

            

def remove_element(el, lst):
    '''
    Remove specific element from list
    '''
    
    return [x for x in lst if x != el]


def from_str_to_array(str):
    '''
    Transform string (array saved in csv) into array
    string format: '[3.05637  5.916344]'
    array format: [3.05637, 5.916344]
    '''

    str0 = str.replace('  ', ', ')
    str1 = np.array(ast.literal_eval(str0))

    return str1


