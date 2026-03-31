import pandas as pd
from pathlib import Path

# set directory
cwd = Path.cwd()
parent_dir = cwd.parent.parent.parent
print(parent_dir)


projects_path = parent_dir / 'Data' / 'project_until_2025_no_nan_obj.csv'
org_8_path = parent_dir / 'Data' / 'organizations' / 'org_8_updated.csv'
org_9_path = parent_dir / 'Data' / 'organizations' / 'org_9_updated.csv'

output_res_path = parent_dir / 'Data' / 'proj_res_H2020_HEU.csv'
output_ind_path = parent_dir / 'Data' / 'proj_ind_H2020_HEU.csv'


projects_df = pd.read_csv(projects_path)
org_8_df = pd.read_csv(org_8_path)
org_9_df = pd.read_csv(org_9_path)
org_8_df['fp'] = 8
org_9_df['fp'] = 9

projects_df['id'] = projects_df['id'].astype(str)
org_8_df['projectID'] = org_8_df['projectID'].astype(str)
org_9_df['projectID'] = org_9_df['projectID'].astype(str)


projects_filtered_df = projects_df[['id', 'fp', 'objective']]
org_8_filtered_df = org_8_df[['projectID', 'organisationID', 'activityType', 'fp']]
org_9_filtered_df = org_9_df[['projectID', 'organisationID', 'activityType', 'fp']]
org_8_filtered_df = org_8_filtered_df.rename(columns={'projectID': 'id'})
org_9_filtered_df = org_9_filtered_df.rename(columns={'projectID': 'id'})

org_8_res_df = org_8_filtered_df[org_8_df['activityType'].isin(['HES', 'REC'])]
org_8_ind_df = org_8_filtered_df[org_8_df['activityType'] == 'PRC']
org_9_res_df = org_9_filtered_df[org_9_df['activityType'].isin(['HES', 'REC'])]
org_9_ind_df = org_9_filtered_df[org_9_df['activityType'] == 'PRC']

org_res_df = pd.concat([org_8_res_df, org_9_res_df])
org_ind_df = pd.concat([org_8_ind_df, org_9_ind_df])

projects_res_df = pd.merge(projects_filtered_df, org_res_df, on=['id', 'fp']).sort_values(by='fp')
projects_ind_df = pd.merge(projects_filtered_df, org_ind_df, on=['id', 'fp']).sort_values(by='fp')

projects_res_df = projects_res_df.drop_duplicates(['id', 'fp'])
projects_ind_df = projects_ind_df.drop_duplicates(['id', 'fp'])

projects_res_df.to_csv(output_res_path)
projects_ind_df.to_csv(output_ind_path)