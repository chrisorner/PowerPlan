import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from energyapp.dashapp1.alpg.helper_func.set_parameters import set_parameters
from energyapp.dashapp1.alpg.profilegenerator import profilegenerator
from energyapp.dashapp1.alpg.helper_func.read_data import read_alpg_data

print('here')

def register_callbacks(dashapp):
    @dashapp.callback(
    Output('graph_loadprofile', 
    'figure'),
    [Input('button_calc', 'n_clicks'),
     Input('checkbox_cons_data', 'value')],
    [State('n_kids', 'value'),
     State('yearly_cons', 'value'),
     State('dist_work', 'value')])
    def setParam(n_clicks, sel_output, n_kids, yearly_cons, dist_work):
        if n_clicks is not None:
            set_parameters(n_kids,yearly_cons,dist_work)
            profilegenerator()

        start = pd.Timestamp('2018-01-01')
        end = pd.Timestamp('2018-12-31 23:59:00')
        data_range = read_alpg_data(start, end)

        #select = (alpg_data.index >= start) & (alpg_data.index <= end)
        #data_range = alpg_data.loc[select]

        traces = []
        for data in sel_output:
            traces.append(go.Scatter(
                    x=data_range.index,
                    y=data_range[data],
                    mode='lines',
                    name= data,
                    marker={
                        'size': 5,
                        'line': {'width': 0.5, 'color': 'blue'}
                    },
                ))

        return {
            'data': traces,
            'layout': go.Layout(
                title='alpg consumer data',
                xaxis={'title': 'Time'},
                yaxis={'title': 'Power Consumption [W]'},
                legend=dict(x=-.1, y=1.2))}