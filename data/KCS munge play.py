
# coding: utf-8

# In[30]:

import pandas
import numpy as np
import matplotlib.pyplot as plt
import os
get_ipython().magic(u'matplotlib inline')


# In[31]:

import getMTAdata as mta
df, links = mta.getAllDf(n_start=0, n_end=1)
filenames = [os.path.split(l)[1] for l in links]
print links
print filenames


# In[32]:

df.head()


# In[33]:

# or we can read from the csv file
# df = pandas.read_csv("Saturday, April 02, 2016") 
df.columns = ['C/A','UNIT','SCP','STATION','LINENAME','DIVISION','DATE','TIME','DESC','IN','OUT']
df = df[['UNIT', 'SCP', 'DATE', 'TIME', "IN", "OUT"]]
df.head(5)


# In[34]:

# Create a coordinates look up table and add a column

geocode = pandas.read_csv('geocoded.csv', header=None)
geocode = geocode.drop_duplicates(0)
geocode = geocode[[0,5,6]]
geocode.columns = ['UNIT', 'LAT', 'LON']
geocode_mapping = {row.values[0]:[row[1], row[2]] for index,row in geocode.iterrows()}

def map(unit):
    try:
        return geocode_mapping[unit]
    except:
        return np.nan

df['COORD'] = df['UNIT'].apply(map)
df['LAT'] = df['COORD'].apply(lambda x: x[0])
df['LON'] = df['COORD'].apply(lambda x: x[1])


# In[35]:

df.head(5)


# In[36]:

#Add the times as datetime objects

import datetime
df["DATETIME"] = df["DATE"]+ ' ' + df["TIME"]
df["DATETIME"] = pandas.to_datetime(df["DATETIME"])

# uncomment below if we want the day to be int
# df["DAY"] = df.DATETIME.apply(lambda x: int(x.weekday()))


# In[37]:

def classify_day(time):
    if time.isoweekday() in range(1,6):
        return "Weekday"
    else:
        return "Weekend"

df["DAY"] = df['DATETIME'].apply(classify_day)


# In[38]:

df.head()


# In[39]:

def classify_time(time):
    if 5 <= time.hour <= 9:
        return "Morning"
    elif 17 < time.hour < 22:
        return "Evening"
    else:
        return None
df["M_E"] = df['DATETIME'].apply(classify_time)


# In[40]:

df.head()


# In[41]:

get_ipython().run_cell_magic(u'time', u'', u"\n# make a group reduce function to apply to df.groupby\ndef group_manipulation(df):\n    reduce_df = pandas.Series()\n    # IN = df.IN.values; OUT = df.OUT.values\n    # IN = IN[1:] - IN[:-1] # convert from cumulative\n    # OUT = OUT[1:] - OUT[:-1]\n    # mask = (IN >= 0) & (IN < 1e4) & (OUT >= 0) & (OUT < 1e4)\n    reduce_df['UNIT'] = df.iloc[0]['UNIT']\n    reduce_df['IN'] = df.IN.sum()\n    reduce_df['OUT'] = df.OUT.sum()\n    reduce_df['LAT'] = df.iloc[0]['LAT']\n    reduce_df['LON'] = df.iloc[0]['LON']\n    return reduce_df")


# In[42]:

# define a model to adjust the outflux to conserve mass
def model_outflux(OUT, adjust=1.33):
    """model to adjust outflux for the purpose of mass conservation"""
    return OUT * adjust


# In[43]:


def getMasterDF(df, target_DAY='Weekday', target_M_E='Morning', adjust=1.33):
    """
        feed orig. dataframe to perform filtering and grouping then return 
        a tableau friendly masterDF 
    """
    # filter df to target day and timeslot
    df = df.copy()
    df = df[df['DAY'] == target_DAY]
    df = df[df['M_E'] == target_M_E]

    # group data by UNIT and apply group operation
    masterDF = df.groupby('UNIT', as_index=False).apply(group_manipulation)
    masterDF['OUTPRIME'] = masterDF['OUT'].apply(
        lambda x: model_outflux(x, adjust)
    )
    masterDF['FOOTTRAFFIC'] = masterDF.IN + masterDF.OUTPRIME
    masterDF['FLUX'] = (masterDF.IN - masterDF.OUTPRIME) / masterDF.FOOTTRAFFIC
        
    
    print "\tsum of IN",  masterDF.IN.sum()
    print "\tsum of OUT", masterDF.OUT.sum()
    ratio = float(masterDF.OUT.sum()) / masterDF.IN.sum()
    print "\tTotal OUT is {:%} of total IN".format(ratio)
    adjust = 1. / ratio
    print "\tan ajustment parameter should be applied: ", adjust
    filename_group = ''.join([f.split('.')[0]  for f in filenames]
                            ) + '_' + target_DAY + '_' + target_M_E +'.csv'
    print 'saving', filename_group
    print
    masterDF.to_csv(filename_group, index_label=None)
    return masterDF


# In[46]:

target_DAYs = ['Weekday', 'Weekend']
target_M_Es = ['Morning', 'Evening']

df['IN'] = np.concatenate([[0], df['IN'].values[1:] - df['IN'].values[:-1]])
df['OUT'] = np.concatenate([[0], df['OUT'].values[1:] - df['OUT'].values[:-1]])
IN = df.IN.values; OUT = df.OUT.values
mask = (IN >= 0) & (IN < 1e4) & (OUT >= 0) & (OUT < 1e4)
df = df[mask]

for target_DAY in target_DAYs:
    for target_M_E in target_M_Es:
        print 'working', target_DAY, target_M_E, '...'
        masterDF = getMasterDF(df, target_DAY, target_M_E, adjust=1.33)


# In[45]:

masterDF[masterDF['UNIT'] == 'R001']
masterDF


# In[34]:

masterDF.head()


# ---
# ### running till the above will generate data for [weekday, weekend][morning, evening]

# In[28]:

get_ipython().run_cell_magic(u'time', u'', u'# --- this is the same as the above cell to group UNIT\n# --- but it is looping instead of applying group function\n\nmasterDF = pandas.DataFrame(columns=[\'UNIT\', \'IN\', \'OUT\', \'COORDS\'])\nDAY = \'Weekday\'\nM_E = "Morning"\ndf[\'IN\'] = np.concatenate([[0], df[\'IN\'].values[1:] - df[\'IN\'].values[:-1]])\ndf[\'OUT\'] = np.concatenate([[0], df[\'OUT\'].values[1:] - df[\'OUT\'].values[:-1]])\nIN = df.IN.values; OUT = df.OUT.values\nmask = (IN >= 0) & (IN < 1e4) & (OUT >= 0) & (OUT < 1e4)\ndf = df[mask]\nfor unit, group in df.groupby([\'UNIT\']):\n    \n    # Filter for weekday mornings\n    day = group[group.DAY == DAY]\n    timeOfDay = day[day.M_E == M_E]\n    masterDF.loc[len(masterDF)] = (unit, timeOfDay.IN.sum(), \n                                   timeOfDay.OUT.sum(), group[\'COORD\'].iloc[0])\n\n\nmasterDF.to_csv("SaturdayApril022016-%s-%s"%(DAY, M_E))')


# In[29]:

masterDF.head()


# In[ ]:

masterDF.sum()


# In[189]:

masterDF.to_csv("SaturdayApril022016-%s-%s"%(DAY, M_E))


# In[132]:

df = df[df['UNIT'] == 'R001']
df['IN_PRIME'] = np.concatenate([[0], df['IN'].values[1:] - df['IN'].values[:-1]])
df['OUT_PRIME'] = np.concatenate([[0], df['OUT'].values[1:] - df['OUT'].values[:-1]])
IN = df.IN_PRIME; OUT = df.OUT_PRIME
mask = (IN >= 0) & (IN < 1e4) & (OUT >= 0) & (OUT < 1e4)
df = df[mask]


# In[188]:

print df[(df.M_E == 'Morning') & (df.DAY == 'Weekday')].sum()

# Filter for weekday mornings
day = df[df.DAY == 'Weekday']
timeOfDay = day[day.M_E == "Morning"]
print timeOfDay.sum()


# In[161]:

df


# In[105]:

df.groupby(df.DATETIME.apply(lambda x: x.hour)).sum().IN_PRIME.plot()
#plt.xlim(datetime.datetime(2016, 3,28,0), datetime.datetime(2016, 3, 29, 0))


# In[191]:

input()


# In[ ]:



