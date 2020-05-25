import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
from joblib import load, dump

import eda

import psycopg2 as pg
import sql_fish

from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, Range1d
from bokeh.layouts import layout
from bokeh.palettes import Spectral3
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from pyproj import Proj, transform
output_file('templates/mapping_targets.html')

# all the preprocessing

model = load("rforest_model_trawler.joblib")
feature_names = ['distance_from_port', 'speed', 'course', 'lat', 
                'lon', 'month', 'weekday', 'hour']

connection = sql_fish.fishing_database()

query_conditions_main = "((is_fishing = 1) OR (is_fishing = 0)) AND (gear_type = 'trawlers')"
query_conditions_noconsensus = "((is_fishing < 1) AND (is_fishing > 0)) AND (gear_type = 'trawlers')"

def random_sample_from_postgres(connection, table, conditions=None, rows=1):
    conditions = "WHERE " + conditions if conditions else ""

    query=f"""
        SELECT *
        FROM  (
            SELECT DISTINCT 1 + trunc(random() * (
                SELECT (reltuples/relpages) * (
                    pg_relation_size('fishingtest') /
                    (current_setting('block_size')::integer)
                )
                FROM pg_class where relname = 'fishingtest'
            ))::integer AS index
            FROM   generate_series(1, 1100) g
            ) r
        JOIN {table} USING (index)
        {conditions}
        LIMIT  {rows} 
        """
    sample_df = pd.io.sql.read_sql(query, connection)
    print(conditions)
    print(sample_df[['index', 'is_fishing', 'timestamp', 'lat', 'lon']])

    return sample_df

#helper function to convert lat/long to easting/northing for mapping
#this relies on functions from the pyproj library
def LongLat_to_EN(long, lat):
    try:
      easting, northing = transform(
        Proj(init='epsg:4326'), Proj(init='epsg:3857'), long, lat)
      return easting, northing
    except:
      return None, None

def update_map(df):
    east_pos, north_pos = LongLat_to_EN(df['lon'].iloc[0], df['lat'].iloc[0])
    
    left = east_pos - 1000000
    right = east_pos + 1000000
    bottom = north_pos - 1000000
    top = north_pos + 1000000

    p = figure(x_range=Range1d(left, right), y_range=Range1d(bottom, top))
    p.add_tile(get_provider(CARTODBPOSITRON))
    p.circle(x=east_pos, y=north_pos, line_color='grey', fill_color='blue', size=10)

    p.axis.visible = False

    save(p)

def grab_random_sample(sample_type=None):

    query_conditions_main = "((is_fishing = 1) OR (is_fishing = 0)) AND (gear_type = 'trawlers')"
    query_conditions_noconsensus = "((is_fishing < 1) AND (is_fishing > 0)) AND (gear_type = 'trawlers')"

    print(sample_type.get('sample_type', 0))
    df = pd.DataFrame()
    while df.empty:
        if sample_type.get('sample_type', 0) == "noconsensus":
            df = random_sample_from_postgres(connection, 'fishingtest', conditions=query_conditions_noconsensus)
        else:
            df = random_sample_from_postgres(connection, 'fishingtest', conditions=query_conditions_main)
    
    df['weekday'] = pd.DatetimeIndex(df['timestamp']).weekday
    update_map(df)
    return df[['is_fishing'] + feature_names]

def make_prediction(feature_dict):
    """
    Input:
    feature_dict: a dictionary of the form {"feature_name": "value"}

    Function makes sure the features are fed to the model in the same order the
    model expects them.

    Output:
    Returns (x_inputs, probs) where
      x_input: a list of feature values in the order they appear in the model
      probs: a list of dictionaries with keys 'name', 'prob'
    """
    print(feature_dict)
    x_input = [float(feature_dict.get(name, 0)) for name in feature_names]
    #x_input = pd.DataFrame(feature_dict)

    pred_probs = model.predict_proba([x_input]).flat
    y_output = float(feature_dict.get('is_fishing', 0))

    probs = [{'name': 'is_fishing', 'prob': pred_probs[0]}]

    return (x_input, y_output, probs)


# This section checks that the prediction code runs properly
# To run, type "python predictor_api.py" in the terminal.
#
# The if __name__='__main__' section ensures this code only runs
# when running this file; it doesn't run when importing
if __name__ == '__main__':
    from pprint import pprint
    print("Checking to see what setting all params to 0 predicts")
    features = {f: '0' for f in feature_names}
    print('Features are')
    pprint(features)

    x_input, probs = make_prediction(features)
    print(f'Input values: {x_input}')
    print('Output probabilities')
    pprint(probs)

first_query = f"SELECT * FROM fishingtest WHERE {query_conditions_main} LIMIT 1;"
first_item = pd.io.sql.read_sql(first_query, connection)
first_item['weekday'] = pd.DatetimeIndex(first_item['timestamp']).weekday
first_item = first_item[feature_names].iloc[0].to_dict()

x_input, actual_fishing, probs = make_prediction(first_item)