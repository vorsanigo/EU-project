import pandas as pd
from shapely.geometry import Point
import geopandas as gpd



def find_nuts3(input_df, nuts3_df, latitude_col, longitude_col, output_file):
    '''
    Function to determine NUTS3 of a place given its geometry
    '''

    # read df files
    '''input_df = pd.read_csv(input_df_path)
    nuts3_df = gpd.read_file(nuts3_df_path)'''

    # create Point geometries from lat/lon
    geometry = [Point(xy) for xy in zip(input_df[longitude_col], input_df[latitude_col])]
    geo_df = gpd.GeoDataFrame(input_df, geometry=geometry, crs="EPSG:4326")

    # filter nuts3 only
    nuts3 = nuts3_df[nuts3_df['LEVL_CODE'] == 3]

    # ensure both datasets use the same crs
    nuts3 = nuts3.to_crs("EPSG:4326")

    # perform spatial join
    joined = gpd.sjoin(geo_df, nuts3, how="left", predicate="within")

    # save file output
    joined.to_csv(output_file, index=False)



#find_nuts3('cleaned organizations/ok organizations/org_geo_8.csv', 'data/NUTS_RG_01M_2013_4326/NUTS_RG_01M_2013_4326.shp', 'lat', 'lon')