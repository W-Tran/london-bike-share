import pandas as pd


def add_daily_future_averages(future, data, col):
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


def sample_future_weather(future, data, col):
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
