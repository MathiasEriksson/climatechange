#%% [markdown]
# # Dependency between the earths temperature and atmospheric C02-levels
# ## This file is an exploration and model building file
# It is intended to be run in VS Code with Jupyter support.
# Read more:https://code.visualstudio.com/docs/python/jupyter-support 
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std

#%% [markdown]
# ## Get data to model the dependency between atmospheric C02 levels and temperatures on earth.
# The data-source for the temperatures is the
# "Estimated Global Land-Surface TAVG based on the Complete Berkeley Dataset"
# provided by Berkley Earth: http://berkeleyearth.org/ .
# The data-source for the C02 levels is the Mauna Loa dataset
# obtained from the National Oceanic and Atmospheric Administration, US Department of Commerce.
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

#%% [markdown]
# Next the 'Year' and 'Month' colums are combined to a pd.Period called 'Time'
# so that it can eventually be used as the index for the dataframe.
#%%
temp_df['Time'] = temp_df[['Year', 'Month']].apply(lambda row: pd.Period(year=row['Year'],month=row['Month'],freq='M') , axis=1)
temp_df.head()

#%% [markdown]
# Now the newly created column can be set as the index and redundant info dropped.

#%%
temp_df = temp_df.set_index('Time')
temp_df = temp_df.drop(['Year',
                        'Month',
                        'Ten-year Anomaly',
                        'T.y. Unc.',
                        'Twenty-year Anomaly','Tw.y. Unc.'],
                         axis=1)
temp_df.head()

#%% [markdown]
# Lets plot some timeseries to gain some understanding about the data

#%%
temp_df.plot(y=['Monthly Anomaly','Annual Anomaly','Five-year Anomaly'],figsize=(15,10))

#%%
temp_df['1998-3-1':].plot(y=['Monthly Anomaly','Annual Anomaly','Five-year Anomaly'],figsize=(15,10))
#%% [markdown]
# There seems to be alot of variance in the data.
# Especially in the Monthly Anomaly series, lets proceed with the more stable
# datasets; Annual Anomaly and Five-year Anomaly.
# Lets next explore possible seasonality and stationarity of the data set.
# Lets explore the autocorrelation and partial autocorrelation functions
# of the "Annual Anomality" and "Five-year Anomaly" to gain more insight into the data.

#%%
plot_acf(temp_df['Annual Anomaly']['1960-3-1':].dropna(axis=0),lags=25);
plot_pacf(temp_df['Annual Anomaly']['1960-3-1':].dropna(axis=0),lags=25);
plot_acf(temp_df['Five-year Anomaly']['1960-3-1':].dropna(axis=0),lags=25);
plot_pacf(temp_df['Five-year Anomaly']['1960-3-1':].dropna(axis=0),lags=25);


#%% [markdown]
# The correlation function show seasonality of one year for the annual series which it should
# at least according to common sense
# since each month value is an anomality in regards to a moving average
# centered around that month and referenced to averages
# estimated from Jan 1951-Dec 1980 monthly absolute temperatures.
# The five year series does not show seasonality which is good since
# seasonality introduces heteroscedasity which is to be avoided.
# The autocorrelation functions for both series shows that there seems to be a trend in the data
# so the series are non-stationary (in other words have a trend).
#
# Lets bring in the data for C02 levels next.
# In this series -99 is used to denote missing data in the average series.

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
#%% [markdown]
# Next the 'Year' and 'Month' colums are combined to a period
# so that it can eventually be used as the index

#%%
co2_df['Time'] = co2_df[['Year', 'Month']].apply(lambda row: pd.Period(year=row['Year'],month=row['Month'],freq='M') , axis=1)
co2_df = co2_df.drop(['Year', 'Month', 'decimal date'],axis = 1)
co2_df = co2_df.set_index('Time')
co2_df.head()

#%%
# Lets again plot the series to gain a better understanding of it
co2_df[co2_df['average'] > -99].plot(y=['average','trend (season corr)'],figsize=(15,10))
co2_df.plot(y=['interpolated'],figsize=(15,10))

#%% [markdown]
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
#%% [markdown]
# After examining plots, acf and pacf plots for both series
# we see that both the CO2 and the temperature data display 
# an increasing trend (backed by acf plots). Additionally the CO2
# shows yearly seasonality in the average and interpolated data columns.
# Based on this the model will be built using the "'Five-year Anomaly'" series
# and the "trend (season corr)" series where the seasonality of the year has been cancelled.
# Next the datasets are combined to one dataframe.

#%%
model_df = pd.merge(co2_df, temp_df, left_index=True, right_index=True)
model_df = model_df.drop(['average',
                          'Annual Anomaly',
                          'interpolated',
                          '#days',
                          'M.A. Unc.',
                          'Monthly Anomaly',
                          'A.A. Unc.',
                          'F.y. Unc.'],
                          axis = 1)
model_df = model_df.dropna(axis=0)
# a const column of 1 has to be added for statsmodels ordinary least squares
# to estimate the intercept
model_df['const'] = 1
model_df.head()

#%%
model_df.plot.scatter('trend (season corr)', 'Five-year Anomaly')

#%%
regr =  sm.OLS(endog=model_df['Five-year Anomaly'], exog=model_df[['const', 'trend (season corr)']], missing='drop')
results = regr.fit()
print(results.summary())
#%% [markdown]
# The regression analysis shows that the R-squared value is 0.955.
# This means that 95% of the variance in five-year average temperature anomalities is 
# explained by the parts per million C02 amount of dried air.
# In other words there is a strong correlation between atmospheric C02 levels and earth temperature.
# This is further confirmed by the F-test for linear regression which claims that there is
# a chance of less tham 0.005 that these result were obtained by chance.
# Next the lets inspect the results with a plot.

#%%
plt.figure(figsize=(8,6))
prstd, iv_l, iv_u = wls_prediction_std(results)
# Plot predicted values
plt.plot(model_df['trend (season corr)'], results.predict(), label='predicted')
# Plot observed values
plt.plot(model_df['trend (season corr)'], model_df['Five-year Anomaly'], label='observed')
#plot confidence intervals
plt.plot(model_df['trend (season corr)'], iv_l,'r--', label='95%-Confidence interval')
plt.plot(model_df['trend (season corr)'], iv_u,'r--')

plt.legend()
plt.title('Temperature change on earth against C02 levels')
plt.xlabel('CO2 fraction in dry air, micromol/mol')
plt.ylabel('Five-year average temperature change')
plt.show()

#%% [markdown]
# ## Predictions about the future
# Lets assume that the C02 levels continue to rise at the same pace
# for the next 20 years what would the temperature on earth be then according to the model.
# lets first examine what the rise in C02 levels have been on average during the last 5 years.

#%%
co2_diff_df = co2_df['2014-1-1':]['trend (season corr)']
co2_diff_df = co2_diff_df.diff().dropna(axis=0)
print('Average increase of C02 per month during the last 5 years:')
print(co2_diff_df.mean())
co2_avg_change = co2_diff_df.mean()

#%% [markdown]
# Lets next extrapolate the increase in C02 for the next 20 years.
# make new df
future_df = co2_df.iloc[-20*12:].copy()
# make new index for 20 years in to the future
future_df['new index'] = co2_df.iloc[-20*12:].index.shift(20*12)
# use the last C02 measurement for starting value for extrapolation
future_df['trend (season corr)'] = co2_df['trend (season corr)'].iloc[-1]
future_df = future_df.assign(trend=np.arange(start= 1,stop=20*12+1))
#Extrapolate
future_df['trend'] = future_df['trend'] * co2_avg_change
future_df['trend (season corr)'] = future_df['trend (season corr)'] +future_df['trend']

# clean up
future_df.index = future_df['new index']
future_df = future_df.drop(['average','interpolated','#days','new index', 'trend'],axis = 1)
future_df.index.rename('Time', inplace= True)
future_df.tail()
#%%
