import textdistance as td
import pandas as pd
import pickle





# strategy 1

'''file = 'analysis/organizations/city_nominatim.csv'

df = pd.read_csv(file)
df_no_nan = df[~df['address'].isna()].reset_index()
df_nan = df[df['address'].isna()].reset_index()

new_df = pd.DataFrame(index=list(df_no_nan['location']), columns=list(df_nan['location']))

count = 0

for col in new_df.columns:
    print(count)
    count += 1
    for i in new_df.index:
        new_df.at[i, col] = td.levenshtein(col, i)

new_df.to_csv('city_dist.csv')'''



# strategy 2


# create dictionary of all distances for cities in same country

'''pickle_file = 'city_country_USE.pickle'
df_file = 'update_4_nominatim_enriched_USE.csv'

with open(pickle_file, 'rb') as file_input:
    country_dict = pickle.load(file_input)
print('pickle', country_dict)

df = pd.read_csv(df_file)

df_no_nan = df[(df['country equal'] == 'nan nominatim') | (df['country equal'] == 'no')].reset_index()
print('d no nan', df_no_nan)

dict_dist = {}
count_no_corr = 0
country_no_corr = []

for i in range(len(df_no_nan)):
    city = df_no_nan.at[i, 'location']
    country = df_no_nan.at[i, 'country_org']
    if country in country_dict.keys():
        for city_ok in country_dict[country]:
            print('city', city)
            print('city ok', city_ok)
            d = td.levenshtein(city, city_ok)
            if not city in dict_dist.keys():
                dict_dist[city] = {}
            dict_dist[city][city_ok] = d
    else:
        count_no_corr += 1
        country_no_corr += [country]

with open('city_dist.pickle', 'wb') as file_output:
    pickle.dump(dict_dist, file_output)
    
print('\n\n')
print('count no corr', count_no_corr)
print('country no corr', country_no_corr)
'''

# find city with smallest distance for each city

with open('city_dist.pickle', 'rb') as file:
    dict_distance = pickle.load(file)

print(len(dict_distance))

df = pd.DataFrame()


for city in dict_distance:
    min_city = []
    min_dist = 1000000
    print('city', city)
    for city_ok in dict_distance[city]:
        print('city ok', city_ok)
        if dict_distance[city][city_ok] < min_dist:
            min_city = [city_ok]
            min_dist = dict_distance[city][city_ok]
        elif dict_distance[city][city_ok] == min:
            min_city += [city_ok]
    df = df._append({'city': city, 'city ok': min_city, 'distance': min_dist}, ignore_index=True)

df.to_csv('dist_city.csv', index=False)

