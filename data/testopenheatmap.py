import pandas as pd
import numpy as np

# this script is used to generate csv file to feed openheatmap
# http://www.openheatmap.com

df0 = pd.read_csv('SaturdayApril022016-Weekday-Mornings', index_col=None)
df = df0[['IN', 'COORDS']].dropna()


def coordstr_to_list(coordstr):
    """ clean up csv file where lists are wrapped as str """
    try:
        return eval(coordstr)
    except (NameError, TypeError):
        return [np.nan, np.nan]


df['COORDS'] = df0.COORDS.apply(coordstr_to_list)
df['lat'] = df.COORDS.apply(lambda x: x[0])
df['lon'] = df.COORDS.apply(lambda x: x[1])
df = df[['IN', 'lat', 'lon']].dropna()
df.to_csv('testheatmap.csv', index_label='index')
