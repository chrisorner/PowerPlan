import pandas as pd
import requests


def get_time_range(start, end, freq):
    # pd.offset to make end date inclusive, tz must be UTC because weather data is UTC
    times = pd.date_range(start=start, end=pd.to_datetime(end) + pd.offsets.Day(), freq=freq, tz="UTC")
    # Don't send the last time which is 0:00 of next day
    times = times[:-1]
    return times


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
    data = {"grant_type": "client_credentials", "client_id": "christians-webapp",
            "client_secret": "77074b1c-a496-4ad2-ac67-34e9bd439733", "scope": "datavalues.read applianceruns.read"}
    token = requests.post(url, headers=headers, data=data).json()
    return token


def get_measured_consumption(token, start, end):
    # Get the total energy consumption
    url = "https://api.smart-vita.de/services/2.0/datarows/91/datavaluepoints/search"
    headers = {"Authorization": f"Bearer {token['access_token']}", "content-type": "application/json"}
    params = {"q": f"cd>{start}+cd<{end}"}
    total_consumption = requests.get(url, headers=headers, params=params).json()
    return total_consumption


def saveToJson(arrays):
    pass
