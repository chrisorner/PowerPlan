import pandas as pd


def get_time_range(start, end, freq):
    # pd.offset to make end date inclusive, tz must be UTC because weather data is UTC
    times = pd.date_range(start=start, end=pd.to_datetime(end) + pd.offsets.Day(), freq=freq, tz="UTC")
    # Don't send the last time which is 0:00 of next day
    times = times[:-1]
    return times
