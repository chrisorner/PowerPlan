import pandas as pd


def read_alpg_data(data_source, start, end, from_json=False):
    """Read alpg output and convert to pandas dataframe"""
    if from_json:
        E_cons = pd.read_json(data_source)
    else:
        E_cons = pd.read_csv(data_source)
    # E_cons['Electronics']=pd.read_csv("energyapp/consumption_profile/alpg/output/results/Electricity_Profile_GroupElectronics.csv")
    # E_cons['Fridge']=pd.read_csv("energyapp/consumption_profile/alpg/output/results/Electricity_Profile_GroupFridges.csv")
    # E_cons['Inductive']=pd.read_csv("energyapp/consumption_profile/alpg/output/results/Electricity_Profile_GroupInductive.csv")
    # E_cons['Lighting']=pd.read_csv("energyapp/consumption_profile/alpg/output/results/Electricity_Profile_GroupLighting.csv")
    # E_cons['Other']=pd.read_csv("energyapp/consumption_profile/alpg/output/results/Electricity_Profile_GroupOther.csv")
    # E_cons['Standby']=pd.read_csv("energyapp/consumption_profile/alpg/output/results/Electricity_Profile_GroupStandby.csv")
    # E_cons['HeatDemand'] = pd.read_csv("energyapp/consumption_profile/alpg/output/results/Heatdemand_Profile.csv")
    # E_cons.index = E_cons.index.map(str)
    date_time = pd.date_range(start='2018-01-01', end='2018-12-31 23:59:00', freq='T')
    E_cons['Time'] = date_time
    E_cons.set_index('Time', inplace=True)

    # start= pd.Timestamp('2018-08-01')
    # end= pd.Timestamp('2018-08-31 23:59:00')
    # end1= pd.Timestamp('2018-08-01 23:59:00')
    select = (E_cons.index >= start) & (E_cons.index <= end)
    data_range = E_cons.loc[select]

    return data_range

# data_range.plot.line()
# data_range['Lighting'].plot.line()

# print(data_range.head())
