import pandas as pd



# read dataframes

h2020 = pd.read_csv('data/H2020/2020/cordis-h2020organizations (copy enriched).csv', sep=';')
fp7 = pd.read_csv('data/FP7/cordis-fp7organizations (copy enriched).csv', sep=';')
fp6 = pd.read_csv('data/FP6/cordis-fp6organizations (copy).csv', sep=';')
fp5 = pd.read_csv('data/FP5/cordis-fp5organizations (copy).csv', sep=';')
fp4 = pd.read_csv('data/FP4/cordis-fp4organizations (copy).csv', sep=';')
fp3 = pd.read_csv('data/FP3/organisation 3 (copy).csv', sep=';')
fp2 = pd.read_csv('data/FP2/organisation 2 (copy).csv', sep=';')
fp1 = pd.read_csv('data/FP1/organisation 1 (copy).csv', sep=';')

datasets_list = [fp1, fp2, fp3, fp4, fp5, fp6, fp7, h2020]


# take pairs org name - city with not nan
sub_df_list = []
tot_df = pd.DataFrame()
count = 0

for df in datasets_list:
    
    count += 1
    str_count = str(count)
    # remove rows with nan name or city
    sub_df = df[~(df['name'].isna() | df['city'].isna())]
    sub_df['name'] = sub_df['name'].map(lambda x: x.lower())
    sub_df['city'] = sub_df['city'].map(lambda x: x.lower())
    # remove rows with name == 'n/a' or 'not available'
    sub_df = sub_df[~((sub_df['name'] == 'n/a') | (sub_df['name'] == 'not available'))]
    # set the programme number
    sub_df['programme'] = str_count
    sub_df = sub_df[['programme', 'name', 'city']]
    sub_df_list += [sub_df]
    tot_df = pd.concat([tot_df, sub_df])

# remove duplicated rows
tot_df = tot_df.drop_duplicates(subset=['name', 'city'])
tot_df.to_csv('nominatim city results/unique_pairs_name_city.csv', index=False)



# read org - city df
df = pd.read_csv('nominatim city results/unique_pairs_name_city.csv')
print(len(df))
df0 = df.drop_duplicates(subset=['name'])
print(len(df0))
# df1 -> with no duplicates at all, we save the ones with more possible city in the next df
df00 = df[~df.duplicated(subset='name', keep=False)]
df00.to_csv('nominatim city results/name_city_removed_all_dupl_name.csv', index=False) # save df1
print(len(df00))
# df2 -> with only the duplicates (we keep duplicates here)
df000 = df[df.duplicated(subset='name', keep=False)]
print(len(df000))
df000.to_csv('nominatim city results/name_city_dupl_keep.csv', index=False) # save df2
# df3 -> with only the duplicates (we keep only one copy for each duplicate)
df0000 = df000.drop_duplicates(subset='name')
print(len(df0000))
df0000.to_csv('nominatim city results/name_city_dupl.csv', index=False) # save df3





# read org - city df
df_org_city = pd.read_csv('nominatim city results/name_city_removed_all_dupl_name.csv')


# read dataframes
h2020 = pd.read_csv('data/H2020/2020/cordis-h2020organizations (copy enriched).csv', sep=';')
fp7 = pd.read_csv('data/FP7/cordis-fp7organizations (copy enriched).csv', sep=';')
fp6 = pd.read_csv('data/FP6/cordis-fp6organizations (copy).csv', sep=';')
fp5 = pd.read_csv('data/FP5/cordis-fp5organizations (copy).csv', sep=';')
fp4 = pd.read_csv('data/FP4/cordis-fp4organizations (copy).csv', sep=';')
fp3 = pd.read_csv('data/FP3/organisation 3 (copy).csv', sep=';')
fp2 = pd.read_csv('data/FP2/organisation 2 (copy).csv', sep=';')
fp1 = pd.read_csv('data/FP1/organisation 1 (copy).csv', sep=';')

datasets_list = [fp1, fp2, fp3, fp4, fp5, fp6, fp7, h2020]

# for each programme, find cities for org with no city
count = 0
for df in datasets_list:
    
    count += 1
    # remove nan org names
    sub_df = df[~(df['name'].isna())]
    sub_df['name'] = sub_df['name'].map(lambda x: x.lower())
    # remove nan org names
    sub_df = sub_df[~((sub_df['name'] == 'n/a') | (sub_df['name'] == 'not available'))]
    # sub df with nan cities
    nan_city_df = sub_df[sub_df['city'].isna()]
    nan_city_df = nan_city_df.drop(columns=['city'])
    # sub df with no nan cities
    city_df = sub_df[~sub_df['city'].isna()]
    
    # merge on org name with the dataset created before of org name - city
    merged = pd.merge(nan_city_df, df_org_city, on='name', how='left')
    merged_tot = pd.concat([merged, city_df])
    
    merged_tot.to_csv('cleaned organizations/' + 'org_' + str(count) + '.csv')