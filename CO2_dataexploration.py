#%% [markdown]
# # Dependency between the earths temperature and atmospheric C02-levels
# ## This file is an exploration and modelbuilding file
# It is intended to be run in VS Code with Jupyter support.
# Read more:https://code.visualstudio.com/docs/python/jupyter-support 
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

#%% [markdown]
# ## Get data to model the dependency between atmospheric C02
# ## levels and temperatures on earth.
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
# Lets plot some timeseries to gain some understanding about the data 
temp_df.plot(y=['Monthly Anomaly','Annual Anomaly'],figsize=(15,10))

#%%
temp_df['1998-3-1':].plot(y=['Monthly Anomaly','Annual Anomaly'],figsize=(15,10))
#%%
# There seems to be alot of variance in the data.
# Lets next explore possible seasonality and stationarity of the data set.
# Lets explore the autocorrelation and partial autocorrelation functions
# of the "Monthly Anomality" to gain more insight into the data.
plot_acf(temp_df['Monthly Anomaly']['1960-3-1':],lags=25);
plot_pacf(temp_df['Monthly Anomaly']['1960-3-1':],lags=25);


#%%
# The correlation functions do not show seasonality which it should not
# since each months value is an anomality in regards to the
# Estimated Jan 1951-Dec 1980 monthly absolute temperature.
# The autocorrelation function shows that there seems to be a trend in the data
# so that the series is non stationary.
#
# Lets bring in the data for C02 levels next.
# In this series -99 is used to denote missing data in the average series

#%%
co2_header = [
    'Year',
    'Month',
    'decimal date',
    'average',
    'interpolated',
    'trend (season corr)',
    '#days'
]
co2_df = pd.read_csv('ftp://ftp.cmdl.noaa.gov/ccg/co2/trends/co2_mm_mlo.txt',
            delim_whitespace=True,
            comment='#',
            header=None,
            names=co2_header
            )
co2_df.head()
#%%
# Next the 'Year' and 'Month' colums are combined to a period
# so that it can eventually be used as the index
co2_df['Time-index'] = co2_df[['Year', 'Month']].apply(lambda row: pd.Period(year=row['Year'],month=row['Month'],freq='M') , axis=1)
co2_df = co2_df.drop(['Year', 'Month', 'decimal date'],axis = 1)
co2_df = co2_df.set_index('Time-index')
co2_df.head()

#%%
# Lets again plot the series to gain a better understanding of it
# Lets plot some timeseries to gain some understanding about the data 
co2_df[co2_df['average'] > -99].plot(y=['average','trend (season corr)'],figsize=(15,10))

#%%
co2_df.plot(y=['interpolated'],figsize=(15,10))

#%%
# Since the data in the interpolated and average are so close
# there seems to be no benefit to using the raw average data since
# it may contain missing data that has to be dealt with. The CO2 data
# shows clear seasonality so to avoid heteroscedasticity 
# we will use the seasonaly corrected trend data series.
# The seasonality will be confirmed by an acf-plot:
#%%
plot_acf(co2_df['interpolated'],lags=25);
plot_pacf(co2_df['interpolated'],lags=25);

#%%
plot_acf(co2_df['trend (season corr)'],lags=25);
plot_pacf(co2_df['trend (season corr)'],lags=25);
#%%
# After examining plots, acf and pacf plots for both series
# we see that both the co2 and the temperature data display 
# an increasing trend (backed by acf plots). Additionally the co2
# shows yearly seasonality in the average and interpolated data columns.
# Based on this the model will be built using the "Montly Anomality" series
# and the "trend (season corr)" series.