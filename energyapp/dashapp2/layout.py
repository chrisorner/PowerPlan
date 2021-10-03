import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from pvlib import pvsystem

all_modules = pvsystem.retrieve_sam(name='SandiaMod')
module_names = list(all_modules.columns)

layout = html.Div([

    dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink('Home Page', href='/', style= {'color': 'white'}, external_link=True)),
                dbc.NavItem(dbc.NavLink('Load Configuration', href='/profile/', style= {'color': 'white'}, external_link=True)),
                dbc.NavItem(dbc.NavLink('Simulation', active=True, href='/simulation/', style= {'color': 'white'}, external_link=True))
            ],
            className= 'navbar navbar-expand-lg navbar-dark bg-dark fixed-top'
        ),

    html.Div([
        html.Div([
            html.H5('Select Graph'),
            dcc.Dropdown(
                id='select_Graph',
                options=[
                    {'label': 'Costs', 'value': 'cost_graph'},
                    {'label': 'Energy Overview', 'value': 'power_graph'}
                ], value= 'cost_graph')
        ], className='col-3'),

    ], className='row'),
    html.Div([
        html.Div([html.Button('Start Calculation', id='button_calc', className='btn btn-primary')], className='col-3')
    ], className='row my-2'),
    html.Div([
        html.Div([
            dcc.Tabs(id="tabs-graph", value='tab-cost', children=[
            dcc.Tab(label='Costs', value='tab-cost', children=[
                html.Div([
                    dcc.Graph(id='graph-with-slider', config={'displayModeBar': False})
                    ])]),

            dcc.Tab(label='Battery Sizes', value='tab-batteries', children=[
                html.Div([
                    dcc.Graph(id='graph-batteries', config={'displayModeBar': False})
                    ])]),

            dcc.Tab(label='Electrical Power', value='tab-power', children=[
                html.Div([
                    dcc.Graph(id='graph_solpower', config={'displayModeBar': False})
                ])]),

            dcc.Tab(label='Optimized Load', value='tab-optimize', children=[
                html.Div([
                    dcc.Graph(id='graph_optimize', config={'displayModeBar': False})
                ])])
            ]),
        html.Div([
            html.Div([html.Button('Create Report', id='button_report', className='btn btn-primary')], className='col-3')
        ], className='row my-2'),

        ], className='col-6'),
        html.Div([
            html.Div([
                html.H4('Energy System', className='col-12'),
                html.Div([
                    html.Label('Solar Panels Area [m2]', id='A_cells_label'),
                    dcc.Input(id='A_cells', value='50', type='text', className='form-control')
                ], className='col-4 offset-md-1'),
                html.Div([
                    html.Label('Battery Capacity [kWh]', id='cap_label'),
                    dcc.Input(id='capacity', value='5', type='text', className='form-control')
                ], className='col-4 offset-md-1')
            ], className='row my-4'),

            html.Div([
                html.Div([
                    html.Label('Solar Panels'),
                    dcc.Dropdown(
                        id='sandia_database',
                        options=[{'label': module, 'value': module} for module in all_modules],
                        value='Canadian_Solar_CS5P_220M___2009_'),
                ], className='col-4')
            ],className='row my-4'),
            html.Div([
                html.Div([
                    html.Label('Panel Tilt [Deg]', id='tilt'),
                    dcc.Input(id='panel_tilt', value='30', type='number', className='form-control')
                ],className='col-3'),
                html.Div([
                    html.Label('Panel Orientation [Deg]', id='orient'),
                    dcc.Input(id='panel_orient', value='180', type='number', className='form-control')
                ],className='col-3'),

            ], className='row my-4 align-items-end'),
            html.Div([
                html.H4('Cost Data', className='col-12'),
                html.Div([
                    html.Label('Battery [EUR/kWh]', id='cost_label'),
                    dcc.Input(id='cost_bat', value='1100', type='text', className='form-control')
                ], className='col-2'),
                html.Div([
                    html.Label('Grid supply [EUR/kWh]', id='cost_label2'),
                    dcc.Input(id='cost_kwh', value='0.3', type='text', className='form-control')
                ], className='col-2'),
                html.Div([
                    html.Label('Solar Panels [EUR/kWp]', id='cost_label3'),
                    dcc.Input(id='cost_wp', value='1000', type='text', className='form-control')
                ], className='col-2'),
                html.Div([
                    html.Label('Number of Years', id='years_label'),
                    dcc.Input(id='years', value='20', type='number', className='form-control')
                ], className='col-2'),
                html.Div([
                    html.Label('Increase of Energy Cost', id='inc_cost_label'),
                    dcc.Input(id='inc_cost_ener', value='0.01', type='text', className='form-control')
                ], className='col-2'),
                html.Div([
                    html.Label('Inflation', id='inflation_label'),
                    dcc.Input(id='inflation', value='0.02', type='text', className='form-control')
                ], className='col-2'),
            ], className='row my-4 align-items-end'),
            html.Div([
                html.H4('Energy System', className='col-12'),
                html.Div([
                    html.Label('Location', id='location_label'),
                    dcc.Input(id='location', type='text', className='form-control', value='Berlin')
                ], className='col-4 offset-md-1'),
                html.Div([
                    html.Div([html.Button('Submit', id='button_loc', className='btn btn-primary')])
                ], className='col-4 offset-md-1')
            ], className='row my-4'),
        ], className='col-6')
    ], className='row'),

    html.Div([
       # html.Div([
       #     html.H4('Energy Consumption Over Day'),
       #     dt.DataTable(
       #         columns=[{"name": i, "id": i} for i in df.columns],
       #         data=df.to_dict("records"),
       #         n_fixed_rows=1,
       #         style_table={'maxHeight': '300', 'overflowY': 'scroll'},
                # optional - sets the order of columns
                # columns=sorted(DF_SIMPLE.columns),
       #         editable=True,
       #         id='editable-table')
        #], className='col-4'),

    ], className='row'),

    html.Div([


        html.P(id='placeholder_database_entry', style={'display': 'none'}),
        html.Div(id= 'placeholder_delete_db',style={'display': 'none'}),
        html.Div(id='placeholder_report', style={'display': 'none'}),
        html.Div(id='store_p_sol', style={'display': 'none'}),
        html.Div(id='store_p_cons', style={'display': 'none'}),
        html.Div(id='store_rad', style={'display': 'none'}),
        html.Div(id='store_e_batt', style={'display': 'none'}),
        html.Div(id='store_e_grid', style={'display': 'none'}),
        html.Div(id='store_e_sell', style={'display': 'none'}),
        html.Div(id='store_grid_costs', style={'display': 'none'}),
        html.Div(id='store_solar_costs', style={'display': 'none'}),
        html.Div(id='store_location', style={'display': 'none'}),
        html.Div(id='store_cost_with_batteries', style={'display': 'none'})
    ], className='row my-4 align-items-end'),



], className='mx-3')
