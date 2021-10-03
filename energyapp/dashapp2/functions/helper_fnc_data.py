import pandas as pd
import datetime
import requests

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
def read_alpg_results(path, column, start="20200101", end="20201231", freq="H"):
    dataset = pd.read_csv(path)
    consumption = dataset.divide(1000)
    data_range = pd.date_range(start=start, end=pd.to_datetime(end) + pd.offsets.Day(), freq='min')
    data_range = data_range[:-1]
    consumption['datetime'] = data_range
    consumption.set_index('datetime', inplace=True)
    consumption_resampled = consumption.resample(freq).mean()
    consumption_numeric = pd.to_numeric(consumption_resampled[column]).values

    return consumption_numeric


def get_token():
    # Get access token
    url = "https://auth.smart-vita.de/token"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    data = {"grant_type":"client_credentials", "client_id":"christians-webapp", "client_secret":"77074b1c-a496-4ad2-ac67-34e9bd439733", "scope":"datavalues.read applianceruns.read"}
    token = requests.post(url, headers=headers, data=data).json()
    return token

def get_consumption(token, start, end):

    # Get the total energy consumption
    url =  "https://api.smart-vita.de/services/2.0/datarows/91/datavaluepoints/search"
    headers = {"Authorization": f"Bearer {token['access_token']}", "content-type": "application/json"}
    params = {"q":f"cd>{start}+cd<{end}"}
    total_consumption = requests.get(url, headers=headers, params=params).json()
    return total_consumption

def saveToJson(arrays):
    pass


