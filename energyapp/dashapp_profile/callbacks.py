import os
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from energyapp.dashapp_profile.alpg.helper_func.set_parameters import set_parameters
from energyapp.dashapp_profile.alpg.profilegenerator import profilegenerator
from energyapp.dashapp_profile.alpg.helper_func.read_data import read_alpg_data

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}


def register_callbacks(dashapp):
    @dashapp.callback(
    Output('generate_profile_output',
    'data'),
    [Input('button_calc', 'n_clicks')],
    [State('n_kids', 'value'),
     State('yearly_cons', 'value'),
     State('dist_work', 'value'),
     State('select_household', 'value')])
    def setParam(n_clicks, n_kids, yearly_cons, dist_work, type_household):
        if n_clicks is not None:
            set_parameters(n_kids,yearly_cons,dist_work, type_household)
            jsonData = profilegenerator()
            df = read_alpg_data(jsonData, pd.Timestamp('2018-01-01'), pd.Timestamp('2018-12-31 23:59:00'), from_json=True)
            df_resampled = df.resample("15min").mean()
            return df_resampled.to_json(orient="columns")


    @dashapp.callback(
        Output('graph_loadprofile',
               'figure'),
        [Input('checkbox_cons_data', 'value'),
        Input('generate_profile_output', 'data')])
    def change_graph(sel_output, profile_generated):

        if profile_generated != None:
            data_range = pd.read_json(profile_generated)
        
        else:

            file = "energyapp/dashapp_profile/alpg/output/results/Electricity_Profile_ForOptimization.csv"
            if os.path.exists(file) and os.stat(file).st_size != 0:
                start = pd.Timestamp('2018-01-01')
                end = pd.Timestamp('2018-12-31 23:59:00')
                data_range = read_alpg_data(file, start, end)
            else:
                date_time = pd.date_range(start='2018-01-01', end='2018-12-31 23:59:00', freq='T')
                data_range = pd.DataFrame(date_time, columns=["Time"])
                data_range['Total'] = pd.Series(np.zeros(len(data_range.index)))
                data_range.set_index('Time', inplace=True)

        # select = (alpg_data.index >= start) & (alpg_data.index <= end)
        # data_range = alpg_data.loc[select]

        traces = []
        for data in sel_output:
            traces.append(go.Scatter(
                x=data_range.index,
                y=data_range[data],
                mode='lines',
                name=data,
                marker={
                    'size': 5,
                    'line': {'width': 0.5, 'color': 'rgba(32, 32, 32, .6)'}
                },
            ))

        return {
            'data': traces,
            'layout': go.Layout(
                xaxis={'title': 'Time'},
                yaxis={'title': 'Power Consumption [W]'},
                plot_bgcolor=app_color["graph_bg"],
                paper_bgcolor=app_color["graph_bg"],
                font={"color": "#fff"},
                legend=dict(x=-.1, y=1.2),
                height=400,
                margin={'t':0})}