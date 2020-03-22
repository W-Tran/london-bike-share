import pandas as pd


def add_daily_future_averages(future, data, col):
    """
    Future numerical regressor values (e.g. temperature) are assumed to be an average of
    previous year's values. For example if it was 6 degrees on 2015-01-01 and 8 degrees
    on 2016-01-01 then the future value is assumed to 6+8/2 = 7 degrees for 2017-01-01.

    When forecasting bike shares for real, this should be replaced by actual weather forecast
    information. Simulated historical forecasts use the actual future regressor values from
    the data.
    """
    future, data = future.copy(), data.copy()
    historical_values = future[future.ds.isin(data.ds)].copy()
    future_values = future[~future.ds.isin(data.ds)].copy()
    historical_values[col] = data[col].values

    future_values['DayOfYear'] = future_values.ds.dt.dayofyear
    data['DayOfYear'] = data.ds.dt.dayofyear
    mean_values = data.groupby(['DayOfYear'])[col].mean().reset_index()
    future_values = future_values.merge(mean_values, on=['DayOfYear'], how='left')
    future_values.drop(columns=['DayOfYear'], inplace=True)

    future[col] = pd.concat([historical_values, future_values])[col].reset_index(drop=True)

    return future


def add_hourly_future_averages(future, data, col):
    """
    Future numerical regressor values (e.g. temperature) are assumed to be an average of
    previous year's values. For example if it was 6 degrees on 2015-01-01 and 8 degrees
    on 2016-01-01 then the future value is assumed to 6+8/2 = 7 degrees for 2017-01-01.

    When forecasting bike shares for real, this should be replaced by actual weather forecast
    information. Simulated historical forecasts use the actual future regressor values from
    the data.
    """
    future, data = future.copy(), data.copy()
    historical_values = future[future.ds.isin(data.ds)].copy()
    future_values = future[~future.ds.isin(data.ds)].copy()
    historical_values[col] = data[col].values

    future_values['DayOfYear'] = future_values.ds.dt.dayofyear
    future_values['TimeOfDay'] = future_values.ds.dt.time
    data['DayOfYear'] = data.ds.dt.dayofyear
    data['TimeOfDay'] = data.ds.dt.time
    mean_values = data.groupby(['DayOfYear', 'TimeOfDay'])[col].mean().reset_index()
    future_values = future_values.merge(mean_values, on=['DayOfYear', 'TimeOfDay'], how='left')
    future_values.drop(columns=['DayOfYear', 'TimeOfDay'], inplace=True)

    future[col] = pd.concat([historical_values, future_values])[col].reset_index(drop=True)

    return future


def sample_future_weather(future, data, col="rain_thunder_snow"):
    """
    Future weather indicators are sampled from previous year's weather data on
    the same days of the year. For example if it rained (7) on 2015-01-01 and was cloudy (4)
    on 2016-01-01 then the future weather for 2017-01-01 will be sampled from {4, 7}.

    When forecasting bike shares for real, this should be replaced by actual weather forecast
    information. Simulated historical forecasts use the actual weather indicators from
    the data.
    """
    future, data = future.copy(), data.copy()
    historical_values = future[future.ds.isin(data.ds)].copy()
    future_values = future[~future.ds.isin(data.ds)].copy()
    historical_values[col] = data[col].values

    future_values['DayOfYear'] = future_values.ds.dt.dayofyear
    data['DayOfYear'] = data.ds.dt.dayofyear
    sample_weather = data.groupby('DayOfYear')[col].apply(pd.DataFrame.sample, n=1).reset_index().drop(
        columns='level_1')
    future_values = future_values.merge(sample_weather, how='left', on='DayOfYear')
    future_values.drop(columns='DayOfYear', inplace=True)

    future[col] = pd.concat([historical_values, future_values])[col].reset_index(drop=True)

    return future
