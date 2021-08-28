import pandas as pd
import datetime

# read household_power_consumption1.csv
def consumer_data(path):
    today = datetime.datetime.today().strftime('2008-%m-%dT00:00')
    time_end = datetime.date.today() + datetime.timedelta(days=5)
    end_time = time_end.strftime('2008-%m-%dT23:00')

    dataset = pd.read_csv(path, header=0, infer_datetime_format=True,
                          parse_dates=['datetime'],
                          index_col=['datetime'])
    # get all observations for the year
    dff = dataset[str(2008)]
    # the .copy prevents chained indexingS
    #result_sel = result['Global_active_power'].copy()
   # result_sel.index.name = 'datetime'
    # print(result08.size)
    #result08_resample = result08.resample('H').mean()
    # power_tot08 = result08.sum()/60
    #result_sel.fillna(0, inplace=True)

    dff2 = dff.loc[today:end_time]
    df_num = pd.to_numeric(dff2['Global_active_power'])
    df_num = df_num.values
    return df_num

# read results from alpg and convert to ndarray with hour intervals
def read_alpg_results(path, column):
    dataset = pd.read_csv(path)
    consumption = dataset.divide(1000)
    data_range = pd.date_range(start='1/1/2020', end='31/12/2020', freq='min')
    data_range = data_range[:-1]
    consumption['datetime'] = data_range
    consumption.set_index('datetime', inplace=True)
    consumption_resampled = consumption.resample('H').mean()
    consumption_numeric = pd.to_numeric(consumption_resampled[column]).values

    return consumption_numeric

def saveToJson(arrays):
    pass


