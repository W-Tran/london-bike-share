import pandas as pd
from sklearn.preprocessing import PowerTransformer


def get_daily_holidays(df):
    holidays = df.reset_index().groupby(pd.Grouper(key='index', freq='D'))[
        'is_holiday'].max().reset_index().rename(columns={'index': 'ds', 'is_holiday': 'holiday'})
    holidays = holidays.drop(index=holidays[holidays.holiday == 0].index)
    holidays = pd.concat((holidays[['holiday']], holidays[['ds']]), axis=1)
    holidays['holiday'] = holidays.holiday.replace({1.0: 'Holiday'}).astype(str)
    holidays['lower_window'] = 0
    holidays['upper_window'] = 0

    # 2015
    holidays.drop(
        index=holidays[(holidays.ds > pd.datetime(2015, 12, 25)) & (holidays.ds < pd.datetime(2016, 1, 1))].index,
        inplace=True)
    holidays.loc[holidays.ds == pd.datetime(2015, 12, 25), 'holiday'] = 'Christmas'
    holidays = holidays.append(pd.DataFrame(
        dict(holiday=['Christmas Eve'], ds=[pd.datetime(2015, 12, 24)], lower_window=[0], upper_window=[0])),
        ignore_index=True)
    holidays.loc[holidays.ds == pd.datetime(2016, 1, 1), 'holiday'] = 'New Years Day'

    # 2016
    holidays.drop(
        index=holidays[(holidays.ds > pd.datetime(2016, 12, 25)) & (holidays.ds < pd.datetime(2017, 1, 1))].index,
        inplace=True)
    holidays.drop(index=holidays[(holidays.ds > pd.datetime(2016, 12, 31))].index, inplace=True)
    holidays = holidays.append(
        pd.DataFrame(dict(holiday=['Christmas'], ds=[pd.datetime(2016, 12, 25)], lower_window=[0], upper_window=[0])),
        ignore_index=True)
    holidays = holidays.append(pd.DataFrame(
        dict(holiday=['Christmas Eve'], ds=[pd.datetime(2016, 12, 24)], lower_window=[0], upper_window=[0])),
        ignore_index=True)
    holidays = holidays.append(
        pd.DataFrame(dict(holiday=['New Years Day'], ds=[pd.datetime(2017, 1, 1)], lower_window=[0], upper_window=[0])),
        ignore_index=True)
    holidays = holidays.sort_values('ds').reset_index(drop=True)
    return holidays


def preprocess_daily(df):
    data = df[['cnt']].resample('D').sum().reset_index()
    data = data.merge(df[['t1', 'hum', 'wind_speed']].resample('D').mean().reset_index(), on='index',
                      how='left')
    data = data.merge(
        df.reset_index().groupby(pd.Grouper(key='index', freq='D'))['weather_code'].max().reset_index(),
        on='index', how='left')
    data.columns = ['ds', 'y'] + data.iloc[:, 2:].columns.tolist()
    data['rain_thunder_snow'] = data['weather_code'].apply(_rain_thunder_snow).astype(int)
    data = data.drop(columns='weather_code')
    return data


def preprocess_hourly(df):
    data = df[['cnt']].reset_index().copy()
    data.columns = ['ds', 'y']
    data.loc[data.y > 6000, 'y'] = None
    yjt = PowerTransformer(method='yeo-johnson', standardize=False)
    data['y'] = yjt.fit_transform(data[['y']])
    data['is_weekend'] = data['ds'].apply(is_weekend)
    data['is_weekday'] = ~data['ds'].apply(is_weekend)
    data['t1'] = df['t1'].values
    data['hum'] = df['hum'].values
    data['wind_speed'] = df['wind_speed'].values
    data['weather_code'] = df['weather_code'].values
    data['rain_thunder_snow'] = data['weather_code'].apply(_rain_thunder_snow).astype(int)
    data.drop(columns='weather_code', inplace=True)
    data['is_weekend'] = data['ds'].apply(is_weekend)
    data['is_weekday'] = ~data['ds'].apply(is_weekend)
    return data, yjt


def _rain_thunder_snow(weather_code):
    return (weather_code == 7) | (weather_code == 10) | (weather_code == 26)


def is_weekend(ds):
    return (ds.dayofweek == 5) | (ds.dayofweek == 6)
