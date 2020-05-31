import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


layout = html.Div([

    dbc.Nav(
        [
        dbc.NavItem(dbc.NavLink('Home Page',  href='/', style= {'color': 'white'})),
        dbc.NavItem(dbc.NavLink('Load Configuration', active=True, href='/apps/app1', style= {'color': 'white'})),
        dbc.NavItem(dbc.NavLink('Simulation', href='/apps/app2', style= {'color': 'white'})),

        ],
        className= 'navbar navbar-expand-lg navbar-dark bg-dark navbar-fixed-top'
    ),

    html.Div([
        html.Div([
            dcc.Tabs(id='tabs', value='tab-required_param', children=[
                dcc.Tab(label='Required Parameters', value='tab-required_param', children=[
                    html.Div([
                        html.Label('Number of Children'),
                        dcc.Input(id='n_kids', value='2', type='text', className='form-control')
                    ], className='row my-4'),
                    html.Div([
                        html.Label('Yearly Energy Consumption'),
                        dcc.Input(id='yearly_cons', value='3500', type='text', className='form-control')
                    ], className='row my-4'),
                    html.Div([
                        html.Label('Distance to Work'),
                        dcc.Input(id='dist_work', value='20', type='text', className='form-control')
                    ], className='row my-4'),
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
                ]),
                dcc.Tab(label='Optional Parameters', value='tab-optional_param', children=[
                    html.Div([
                        html.Label('Workday Wake-Up Time'),
                        dcc.Input(id='t_wakeup', value='7', type='text', className='form-control')
                    ], className='row my-4'),
                    html.Div([
                        html.Label('Workday Leave for Work'),
                        dcc.Input(id='t_leaveWork', value='8', type='text', className='form-control')
                    ], className='row my-4'),
                    html.Div([
                        html.Label('Time Spent at Work'),
                        dcc.Input(id='t_atWork', value='8.5', type='text', className='form-control')
                    ], className='row my-4'),
                    html.Div([
                        html.Label('Workday Bedtime'),
                        dcc.Input(id='t_bed', value='23', type='text', className='form-control')
                    ], className='row my-4'),
                    html.Div([
                        html.Label('Weekend Wake-Up TIme'),
                        dcc.Input(id='t_wakeup_we', value='9', type='text', className='form-control')
                    ], className='row my-4'),
                    html.Div([
                        html.Label('Weekend Bedtiem'),
                        dcc.Input(id='t_bed_we', value='24', type='text', className='form-control')
                    ], className='row my-4')
                ]),
            ]),

            html.Div([html.Button('Start Calculation', id='button_calc', className='btn btn-primary')], className='col-3 mt-4')
        ], className='col-4 offset-md-1'),
        html.Div([
            dcc.Graph(id='graph_loadprofile', config={'displayModeBar': False})
        ], className='col-5'),
        html.Div([

            dcc.Checklist(id='checkbox_cons_data',
                          options=[
                              {'label': ' Total Energy', 'value': 'Total'},
                              {'label': ' Electronics', 'value': 'Electronics'},
                              {'label': ' Fridge', 'value': 'Fridge'},
                              {'label': ' Inductive', 'value': 'Inductive'},
                              {'label': ' Lighting', 'value': 'Lighting'},
                              {'label': ' Other', 'value': 'Other'},
                              {'label': ' Standby', 'value': 'Standby'}
                          ], value=['Total'],
                          style={'width': '50%', 'height': '100%'},
                          labelStyle={'display': 'block'})
        ],className='col-2'),
    ], className='row'),




    html.Div(id='app-1-display-value')
])
