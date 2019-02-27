#%% [markdown]
# # Dependency between the earths temperature and atmospheric C02-levels
# ## This file is an exploration and modelbuilding file
# It is intended to be run in VS Code with Jupyter support.
# Read more:https://code.visualstudio.com/docs/python/jupyter-support 
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import urllib

#%% [markdown]
# ## Get data to model the dependency between atmospheric C02
# levels and temperatures on earth.
# The data-source for the temperatures is the
# "Estimated Global Land-Surface TAVG" based on the Complete Berkeley Dataset
# provided by Berkley Earth: http://berkeleyearth.org/
# The data-source for the C02 levels is the Mauna Loa dataset
# obtained from the National Oceanic and Atmospheric Administration,
#  US Department of Commerce.
# C02 data: ftp://ftp.cmdl.noaa.gov/ccg/co2/trends/co2_mm_mlo.txt , 
# Temp data: http://berkeleyearth.lbl.gov/auto/Global/Complete_TAVG_complete.txt

#%%
temp_header = [
    'Year',
    'Month',
    'Monthly Anomaly',
    'M.A. Unc.',
    'Annual Anomaly',
    'A.A. Unc.',
    'Five-year Anomaly',
    'F.y. Unc.',
    'Ten-year Anomaly',
    'T.y. Unc.',
    'Twenty-year Anomaly',
    'Tw.y. Unc.'
]
temp_df = pd.read_csv('http://berkeleyearth.lbl.gov/auto/Global/Complete_TAVG_complete.txt',
            delim_whitespace=True,
            comment='%',
            header=None,
            names=temp_header
            )
temp_df.head()

#%%
# Next the 'Year' and 'Month' colums are combined to a period
# so that it can eventually be used as the index
temp_df['Time-index'] = temp_df[['Year', 'Month']].apply(lambda row: pd.Period(year=row['Year'],month=row['Month'],freq='M') , axis=1)
temp_df.head()

#%%
# Now the newly created column can be set as the index and redundant info dropped
# we will focus on monthly and annual anomalities so multi-year info will also be dropped
temp_df = temp_df.set_index('Time-index')
temp_df = temp_df.drop(['Year',
                        'Month',
                        'Five-year Anomaly',
                        'F.y. Unc.',
                        'Ten-year Anomaly',
                        'T.y. Unc.',
                        'Twenty-year Anomaly','Tw.y. Unc.'],
                         axis=1)
temp_df.head()

#%%
