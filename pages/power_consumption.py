import os

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, State, callback
from dash import dcc, html

from energyapp.dashapp_profile.alpg.helper_func.read_data import read_alpg_data
from energyapp.dashapp_profile.alpg.helper_func.set_parameters import set_parameters
from energyapp.dashapp_profile.alpg.profilegenerator import profilegenerator

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

dash.register_page(__name__, path="/powerconsumption", title="Power Consumption", name="Power Consumption")

navbar = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink('Home Page', href='/', style={'color': 'white'}, external_link=True)),
        dbc.NavItem(
            dbc.NavLink('Load Configuration', active=True, href='/powerconsumption', style={'color': 'white'},
                        external_link=True)),
        dbc.NavItem(
            dbc.NavLink('Simulation', href='/solarpower', style={'color': 'white'}, external_link=True)),

    ],
    class_name='navbar navbar-expand-lg navbar-dark bg-dark fixed-top'
)

layout = html.Div([

    navbar,

    html.Div([
        dbc.Row([
            dbc.Col([
                dcc.Tabs(id='tabs', value='tab-required_param', parent_className='custom-tabs',
                         className='custom-tabs-container', children=[
                        dcc.Tab(label='Required Params', value='tab-required_param', className='custom-tab',
                                selected_className='custom-tab--selected', children=[
                                html.Div([
                                    dbc.Row([
                                        html.Div([
                                            html.Label('Select Type of Household'),
                                            dcc.Dropdown(
                                                id='select_household',
                                                options=[
                                                    {'label': 'Single Worker', 'value': 'single_work'},
                                                    {'label': 'Single Retired', 'value': 'single_retired'},
                                                    {'label': 'Dual Worker', 'value': 'dual_work'},
                                                    {'label': 'Dual Retired', 'value': 'dual_retired'},
                                                    {'label': 'Family Dual Worker', 'value': 'fam_dual_work'}
                                                ], value='fam_dual_work')
                                        ])
                                    ], class_name='my-4'),
                                    dbc.Row([
                                        dbc.Label('Number of Children', html_for='n_kids'),
                                        dbc.Input(id='n_kids', value='2', type='text')
                                    ], class_name='my-4'),
                                    dbc.Row([
                                        dbc.Label('Yearly Energy Consumption', html_for='yearly_cons'),
                                        dbc.Input(id='yearly_cons', value='3500', type='text')
                                    ], class_name='my-4'),
                                    dbc.Row([
                                        dbc.Label('Distance to Work', html_for='dist_work'),
                                        dbc.Input(id='dist_work', value='20', type='text')
                                    ], class_name='my-4')

                                ], className='form-group')
                            ]),
                        dcc.Tab(label='Optional Parameters', value='tab-optional_param', className='custom-tab',
                                selected_className='custom-tab--selected', children=[
                                dbc.Row([
                                    dbc.Label('Workday Wake-Up Time', html_for='t_wakeup'),
                                    dbc.Input(id='t_wakeup', value='7', type='text')
                                ], class_name='my-4'),
                                dbc.Row([
                                    dbc.Label('Workday Leave for Work', html_for='t_leaveWork'),
                                    dbc.Input(id='t_leaveWork', value='8', type='text')
                                ], class_name='my-4'),
                                dbc.Row([
                                    dbc.Label('Time Spent at Work', html_for='t_atWork'),
                                    dbc.Input(id='t_atWork', value='8.5', type='text')
                                ], class_name='my-4'),
                                dbc.Row([
                                    dbc.Label('Workday Bedtime', html_for='t_bed'),
                                    dbc.Input(id='t_bed', value='23', type='text')
                                ], class_name='my-4'),
                                dbc.Row([
                                    html.Label('Weekend Wake-Up TIme'),
                                    dcc.Input(id='t_wakeup_we', value='9', type='text', className='form-control')
                                ], class_name='my-4'),
                                dbc.Row([
                                    html.Label('Weekend Bedtiem'),
                                    dcc.Input(id='t_bed_we', value='24', type='text', className='form-control')
                                ], class_name='my-4')
                            ]),
                    ]),

                dbc.Row([
                    dbc.Button('Start Calculation', id='button_calc'),
                    dcc.Loading(
                        id="loading-1",
                        type="default",
                        fullscreen=True,
                        children=dcc.Store(id="generate_profile_output")
                    )
                ], class_name='my-4')
            ], width=2, class_name='mx-1 graph__container'),
            dbc.Col([
                dcc.Graph(id='graph_loadprofile',
                          config={'displayModeBar': False},
                          className='mt-5',
                          figure=dict(
                              layout=dict(
                                  plot_bgcolor=app_color["graph_bg"],
                                  paper_bgcolor=app_color["graph_bg"],
                                  font={"color": "#fff"},

                              )
                          )
                          ),
            ], width=7, className='mx-1 graph__container'),
            dbc.Col([
                dcc.Checklist(id='checkbox_cons_data',
                              options=[
                                  {'label': ' Total Energy', 'value': 'Total'},
                                  {'label': ' Electronics', 'value': 'Electronics'},
                                  {'label': ' Fridges', 'value': 'Fridges'},
                                  {'label': ' Inductive', 'value': 'Inductive'},
                                  {'label': ' Lighting', 'value': 'Lighting'},
                                  {'label': ' Other', 'value': 'Other'},
                                  {'label': ' Standby', 'value': 'Standby'},
                                  {'label': ' HeatDemand', 'value': 'HeatDemand'}
                              ], value=['Total'],
                              labelStyle={'display': 'block'})
            ], width=2, class_name='mx-1 graph__container'),
        ], style={'paddingTop': '70px'})
    ], className='container'),

    # html.Div(id='generate_profile_output'),
    html.Div(id='app-1-display-value')
])


@callback(
    Output('generate_profile_output',
           'data'),
    [Input('button_calc', 'n_clicks')],
    [State('n_kids', 'value'),
     State('yearly_cons', 'value'),
     State('dist_work', 'value'),
     State('select_household', 'value')])
def setParam(n_clicks, n_kids, yearly_cons, dist_work, type_household):
    if n_clicks is not None:
        set_parameters(n_kids, yearly_cons, dist_work, type_household)
        jsonData = profilegenerator()
        df = read_alpg_data(jsonData, pd.Timestamp('2018-01-01'), pd.Timestamp('2018-12-31 23:59:00'), from_json=True)
        df_resampled = df.resample("15min").mean()
        return df_resampled.to_json(orient="columns")


@callback(
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
            margin={'t': 0})}
