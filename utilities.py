# Python Packages
import os
import pandas as pd
import geopandas as gpd


####### Helper Functions

# Used during DB Querying
def convert_row_to_dict(row, Table):
    '''
    Convert an SQLAlchemy Row into a Dictionary
    '''
    lst_of_col = [col.name for col in Table.__table__.columns]

    if type(row) == Table:  # Row obtained from .get()
        dct = { col : getattr(row, col) for col in lst_of_col}
        return dct

    # Obtains from Rows obtained from .all()
    obj = list(dict(row._mapping).values())[0]
    dct = { col : getattr(obj, col) for col in lst_of_col}

    return dct
    

def format_address_name(block, building, postal_code, street):
    '''
    Function used to Clean Address from Recycling Bins Shapefile
    '''
    address = ""
    if block:
        address += f"Blk {block}, "
    if building:
        if "HDB-" in building:
            building = building.replace("HDB-", "").strip()
            if street:
                address += street.title() + ", " + building.title() + ", "
            else:
                address += building + ", "
        else:
            address += building.title() + ", "
            
            if street:
                address += street.title() + ", "
    else:
        if street:
                address += street.title() + ", "

    if postal_code:
        address += f"Singapore {str(postal_code)}"
    return address.strip()


'''
Function used to generate Bins DataFrame
'''
def generate_bins_gdf():
    # Load Data File into GDF
    data_folder = os.path.join(os.getcwd(), "data")
    shapefile_folder = os.path.join(data_folder, "recycling-bins-shp")
    bins_file_name = "RECYCLINGBINS.shp"
    bins_file_path = os.path.join(shapefile_folder, bins_file_name)
    gdf_bins = gpd.read_file(bins_file_path, crs='epsg:4326')

    # Data Cleaning
    columns_needed = [
        "OBJECTID",
        "ADDRESSBLO",
        "ADDRESSBUI",
        "ADDRESSPOS",
        "ADDRESSSTR",
        "geometry"
    ]
    gdf_bins = gdf_bins[columns_needed].copy()
    gdf_bins["location"] = gdf_bins[["ADDRESSBLO", "ADDRESSBUI", "ADDRESSPOS", "ADDRESSSTR"]].apply(
        lambda x: format_address_name(x["ADDRESSBLO"], x["ADDRESSBUI"], x["ADDRESSPOS"], x["ADDRESSSTR"]), axis=1
    )

    gdf_bins = gdf_bins.to_crs("epsg:4326")
    gdf_bins["longitude"] = gdf_bins["geometry"].x
    gdf_bins["latitude"] = gdf_bins["geometry"].y
    gdf_upload = gdf_bins[["OBJECTID", "location", "longitude", "latitude", "geometry"]].rename(columns={"OBJECTID": "id"})
    return gdf_upload

BINS_GDF = generate_bins_gdf()


def find_nearest_bin_location(gdf_bins, lon, lat):
    '''
    Find the nearest bin location given the BINS_GDF, user geolocation
    '''
    # Convert lat lon into GDF
    df_user_location = pd.DataFrame({"longitude": [lon], "latitude": [lat]})
    gdf_user_location = gpd.GeoDataFrame(df_user_location, geometry=gpd.points_from_xy(df_user_location.longitude, df_user_location.latitude), crs="epsg: 4326")
    
    # Use DataFrame Merging and GeoSeries Distance to calculate Distance 
    gdf_user_location["key"] = 1
    gdf_bins["key"] = 1
    merged_gdf = pd.merge(gdf_user_location, gdf_bins, on="key").drop("key", 1)
    gs_user_location = gpd.GeoSeries(merged_gdf['geometry_x'], crs='EPSG:4326').to_crs('EPSG:24500')
    gs_bins = gpd.GeoSeries(merged_gdf['geometry_y'], crs='EPSG:4326').to_crs('EPSG:24500')
    merged_gdf["distance"] = gs_user_location.distance(gs_bins)

    # Return Nearest Bin Location
    nearest = merged_gdf.sort_values(['distance'], ascending=True).head(1).iloc[0, :]

    return nearest.location, nearest.longitude_y, nearest.latitude_y


