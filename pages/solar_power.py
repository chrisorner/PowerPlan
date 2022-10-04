import json
import os

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
from pvlib import pvsystem

from energyapp.dashapp_simulation.Battery import Battery
from energyapp.dashapp_simulation.Costs import Costs
from energyapp.dashapp_simulation.Solar import Solar, P_RADIATION
from energyapp.dashapp_simulation.functions.helper_fnc_calc import get_time_range
from energyapp.dashapp_simulation.functions.helper_fnc_data import read_alpg_results

all_modules = pvsystem.retrieve_sam(name='SandiaMod')
module_names = list(all_modules.columns)

dash.register_page(__name__, path="/solarpower", title="Solar Power Calculator", name="Solar Power Calculator")

graph_selection = dbc.Row(html.Div([
    dbc.Col(html.Div([
        html.H5('Select Graph'),
        dcc.Dropdown(
            id='select_Graph',
            options=[
                {'label': 'Costs', 'value': 'cost_graph'},
                {'label': 'Energy Overview', 'value': 'power_graph'}
            ], value='cost_graph')
    ]), width=3),

], style={'paddingTop': '60px'}))

navbar = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink('Home Page', href='/', style={'color': 'white'}, external_link=True)),
        dbc.NavItem(dbc.NavLink('Load Configuration', href='/powerconsumption', style={'color': 'white'},
                                external_link=True)),
        dbc.NavItem(dbc.NavLink('Simulation', active=True, href='/solarpower', style={'color': 'white'},
                                external_link=True))
    ],
    class_name='navbar navbar-expand-lg navbar-dark bg-dark fixed-top'
)

graphs = dbc.Col(
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
                ])])
        ]),

    ]), width=6
)

controls = dbc.Col([
    dbc.Row([
        html.H4('Energy System'),
        dbc.Col([
            dbc.Label('Solar Panels Area [m2]', html_for="A_cells"),
            dbc.Input(id='A_cells', value='50', type='text')
        ], width=4, class_name='offset-md-1'),
        dbc.Col(html.Div([
            dbc.Label('Battery Capacity [kWh]', html_for="capacity"),
            dbc.Input(id='capacity', value='5', type='text')
        ]), width=4, class_name='offset-md-1')
    ], class_name="my-4"),

    dbc.Row([
        dbc.Col(html.Div([
            html.Label('Solar Panels'),
            dcc.Dropdown(
                id='sandia_database',
                options=[{'label': module, 'value': module} for module in all_modules],
                value='Canadian_Solar_CS5P_220M___2009_'),
        ]), width=4)
    ], class_name='my-4'),
    dbc.Row([
        dbc.Col([
            dbc.Label('Panel Tilt [Deg]', html_for='panel_titl'),
            dbc.Input(id='panel_tilt', value='30', type='number')
        ], width=3),
        dbc.Col([
            dbc.Label('Panel Orientation [Deg]', html_for='panel_orient'),
            dbc.Input(id='panel_orient', value='180', type='number')
        ], width=3),
        dbc.Col([
            dbc.Label('Location', id='location_label'),
            dbc.Input(id='location', type='text', value='Berlin')
        ], width=3)

    ], class_name='my-4 align-items-end'),
    dbc.Row([
        html.H4('Cost Data'),
        dbc.Col([
            dbc.Label('Battery [EUR/kWh]', html_for='cost_battery_specific'),
            dbc.Input(id='cost_battery_specific', value='1100', type='text')
        ], width=2),
        dbc.Col([
            dbc.Label('Grid supply [EUR/kWh]', html_for='cost_kwh'),
            dbc.Input(id='cost_kwh', value='0.3', type='text')
        ], width=2),
        dbc.Col([
            dbc.Label('Solar Panels [EUR/kWp]', html_for='cost_solar_panel'),
            dbc.Input(id='cost_solar_panel', value='1000', type='text')
        ], width=2),
        dbc.Col([
            dbc.Label('Number of Years', html_for='years'),
            dbc.Input(id='years', value='20', type='number')
        ], width=2),
        dbc.Col([
            dbc.Label('Increase of Energy Cost', html_for='cost_energy_increase'),
            dbc.Input(id='cost_energy_increase', value='0.01', type='text')
        ], width=2),
        dbc.Col(html.Div([
            dbc.Label('Inflation', html_for='inflation'),
            dbc.Input(id='inflation', value='0.02', type='text')
        ]), width=2),
    ], class_name='my-4 align-items-end'),
    dbc.Row([
        dbc.Button('Submit', id='button_loc', style={"width": "150px"})
    ], class_name='my-4'),
], width=6)

layout = html.Div([

    navbar,
    graph_selection,

    dbc.Row(html.Div([
        dbc.Col(html.Div([dbc.Button('Start Calculation', id='button_calc')]), width=3)
    ]), class_name="my-2"),
    dbc.Row([
        graphs,
        controls
    ]),

    html.Div([

        html.P(id='placeholder_database_entry', style={'display': 'none'}),
        html.Div(id='placeholder_delete_db', style={'display': 'none'}),
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

startTime = "20180101"
endTime = "20181231"
freq = "H"

# load energy constumption data
consumption_profile = 'energyapp/dashapp_profile/alpg/output/results/Electricity_Profile_ForOptimization.csv'
if os.path.exists(consumption_profile) and os.stat(consumption_profile).st_size != 0:
    P_cons_el = read_alpg_results(consumption_profile, "Total", start=startTime, end=endTime, freq=freq)
    P_cons_heat = read_alpg_results(consumption_profile, "HeatDemand", start=startTime, end=endTime, freq=freq)
else:
    P_cons_el = np.zeros(8760)
    P_cons_heat = np.zeros(8760)


@callback(
    Output('store_location', 'children'),
    [Input('button_loc', 'n_clicks')],
    [State('location', 'value')])
def change_loc(n_clicks, location):
    return location


@callback(

    [Output('store_p_sol', 'children'),
     Output('store_p_cons', 'children'),
     Output('store_rad', 'children'),
     Output('store_e_batt', 'children'),
     Output('store_e_grid', 'children'),
     Output('store_e_sell', 'children'),
     Output('store_grid_costs', 'children'),
     Output('store_solar_costs', 'children'),
     Output('store_cost_with_batteries', 'children')],
    [Input('sandia_database', 'value'),
     Input('store_location', 'children'),
     Input('button_calc', 'n_clicks')],
    [State('cost_battery_specific', 'value'),
     State('capacity', 'value'),
     State('years', 'value'),
     State('cost_kwh', 'value'),
     State('cost_solar_panel', 'value'),
     State('A_cells', 'value'),
     State('panel_tilt', 'value'),
     State('panel_orient', 'value'),
     State('cost_energy_increase', 'value'),
     State('inflation', 'value'),
     ],
)
def update_cost(module, loc, n_clicks, cost_battery_specific, battery_capacity, years_input, cost_kwh, cost_solar_panel,
                roof_area, tilt, surface_azimuth, cost_el_increase, inflation):
    ##Update everything with input data
    Temp = 298  # Ambient Temperature
    years_input = int(years_input)

    cost_battery_total = float(cost_battery_specific) * float(battery_capacity)

    # Solar Model
    cost_el_increase = float(cost_el_increase)
    inflation = float(inflation)

    solar = Solar(float(roof_area), float(tilt), float(surface_azimuth), module)
    solar.get_coordinates(loc)
    time_range = get_time_range(startTime, endTime, freq)
    irradiation, weather, am_abs, aoi = solar.calc_irrad(time_range)
    irrad_global = irradiation['poa_global']
    P_solar = solar.pv_system(irradiation, weather, am_abs, aoi)
    irrad_global_resampled = solar.get_resampled_irradiation(irrad_global, time_range, freq)
    P_solar_resampled = solar.get_resampled_solar_power(P_solar, time_range, freq)

    # Cost Model
    P_peak = float(roof_area) * solar.efficiency * P_RADIATION
    battery = Battery(float(battery_capacity))
    battery.calc_soc(P_cons_el, P_solar_resampled)
    P_store = battery.get_stored_energy()
    P_grid = battery.get_from_grid()
    P_sell = battery.get_w_unused()

    cost = Costs(irrad_global_resampled, years_input, cost_kwh, P_peak, cost_el_increase, inflation)
    cost.calc_costs(irrad_global_resampled, years_input, cost_battery_total, P_peak, cost_solar_panel, P_cons_el,
                    P_grid, P_sell)
    grid_costs = cost.total_costs
    solar_costs = cost.total_costs_sol

    costs_with_batteries = cost.compare_battery_costs(P_cons_el, P_solar_resampled, irrad_global_resampled, years_input,
                                                      float(cost_battery_specific), P_peak, cost_solar_panel)

    exportJson = False

    if exportJson:
        temp = np.ones(8760) * 10
        elec_price_in = np.ones(8760) * 0.30
        gas_price = np.ones(8760) * 0.07
        elec_price_out = np.ones(8760) * 0.11
        ev_aval = np.ones(8760)
        data = np.stack(
            (temp, P_solar_resampled, P_cons_heat, P_cons_el, elec_price_in, gas_price, elec_price_out, ev_aval),
            axis=1)
        df = pd.DataFrame(data, columns=["temperature", "solar_power", "P_cons_heat", "P_cons_el", "ele_price_in",
                                         "gas_price", "ele_price_out", "ev_aval"])
        df_selected = df.iloc[0:48]
        # df_json = df.to_json(surface_azimuth="columns")
        df_json = df_selected.to_json(orient="columns")
        with open("data.json", "w") as jsonFile:
            jsonFile.write(df_json)

    return json.dumps(P_solar_resampled.tolist()), json.dumps(P_cons_el.tolist()), json.dumps(
        irrad_global_resampled.tolist()), \
           json.dumps(P_store.tolist()), json.dumps(P_grid.tolist()), json.dumps(P_sell.tolist()), \
           json.dumps(grid_costs.tolist()), json.dumps(solar_costs.tolist()), json.dumps(
        costs_with_batteries.tolist())


@callback(

    Output('graph_solpower', 'figure'),
    [Input('store_p_sol', 'children')])
def solar_power(sol_power_json):
    try:
        sol_power = json.loads(sol_power_json)
    except TypeError:
        sol_power = np.zeros(8785)

    rad_time = list(range(1, 8785))
    trace1 = []
    trace1.append(go.Scatter(
        x=rad_time[0:8000],
        y=sol_power[0:8000],
        mode='lines',
        marker={
            'size': 5,
            'line': {'width': 0.5, 'color': 'blue'}
        }
    ))

    return {
        'data': trace1,
        'layout': go.Layout(
            title='Solar Power',
            xaxis={'title': 'Time [h]'},
            yaxis={'title': 'Power [W]'},
            legend=dict(x=-.1, y=1.2))
    }


@callback(
    Output('graph-batteries', 'figure'),
    # [Input('button_calc', 'n_clicks')],
    [Input('store_cost_with_batteries', 'children')])
def batterie_costs(costs_batteries_json):
    if costs_batteries_json:
        batteries_list = json.loads(costs_batteries_json)
        batteries = np.array(batteries_list)
        years = list(range(0, 21))
        trace = []
        for i in range(np.size(batteries, 1)):
            trace.append(go.Scatter(
                x=years,
                y=batteries[:, i],
                mode='lines',
                marker={
                    'size': 5,
                    'line': {'width': 0.5}
                },
                name=f'{i + 1}kw',
            ))

        return {
            'data': trace,
            'layout': go.Layout(
                title='Solar Power',
                xaxis={'title': 'Years'},
                yaxis=dict(title='Costs [EUR]', range=[0, 30000]),
                legend=dict(x=-.1, y=1.2, orientation='h'))
        }


@callback(
    Output('graph-with-slider', 'figure'),
    [Input('select_Graph', 'value'),
     Input('years', 'value'),
     Input('store_rad', 'children')],
    [State('store_e_batt', 'children'),
     State('store_e_grid', 'children'),
     State('store_e_sell', 'children'),
     State('store_grid_costs', 'children'),
     State('store_solar_costs', 'children')],
)
def update_graph_costs(sel_plot, years_input, rad_val_json, e_batt_json, e_grid_json, e_sell_json, grid_costs_json,
                       solar_costs_json):
    traces = []

    try:
        rad_val = json.loads(rad_val_json)
        P_store = json.loads(e_batt_json)
        P_grid = json.loads(e_grid_json)
        P_sell = json.loads(e_sell_json)
        grid_costs = json.loads(grid_costs_json)
        solar_costs = json.loads(solar_costs_json)
    except TypeError:
        rad_val = np.zeros(8785)
        P_store = np.zeros(8785)
        P_grid = np.zeros(8785)
        P_sell = np.zeros(8785)
        grid_costs = np.zeros(21)
        solar_costs = np.zeros(21)

    years = int(years_input)

    # rad_time = np.linspace(1, 8760 * years, 8760)
    rad_time = list(range(0, 8785))
    #    t_len = len(rad_val)
    #    d_len = int(t_len / 24)

    # Create Graphs
    traces = []
    traces.append(go.Scatter(
        x=list(range(0, years + 1)),
        y=grid_costs,
        mode='lines',
        name='Cost without Solar Panels',
        marker={
            'size': 5,
            'line': {'width': 0.5, 'color': 'blue'}
        }
    ))

    traces.append(go.Scatter(
        x=list(range(0, years + 1)),
        y=solar_costs,
        mode='lines',
        name='Cost with Solar Panels',
        marker={
            'size': 5,
            'line': {'width': 0.5, 'color': 'blue'}
        }
    ))
    data = list(traces[0:2])
    layout = go.Layout(
        xaxis={'title': 'Years'},
        yaxis={'title': 'Costs [EUR]'},
        legend=dict(x=-.1, y=1.2),
        plot_bgcolor='white')
    fig = go.Figure(data, layout)

    traces.append(go.Scatter(
        x=rad_time[0:119],
        y=P_store[0:119],
        name='Energy Stored',
        mode='lines',
        marker={
            'size': 15,
            'line': {'width': 0.5, 'color': 'white'}
        }
    ))

    traces.append(go.Scatter(
        x=rad_time[0:119],
        y=P_grid[0:119],
        name='Energy Bought',
        mode='lines',
        marker={
            'size': 15,
            'line': {'width': 0.5, 'color': 'green'}
        },
    ))

    traces.append(go.Scatter(
        x=rad_time[0:119],
        y=P_sell[0:119],
        name='Energy Sold',
        mode='lines',
        marker={
            'size': 15,
            'line': {'width': 0.5, 'color': 'green'}
        },
    ))

    traces.append(go.Scatter(
        x=rad_time[0:8784],
        y=rad_val[0:8784],
        name='Radiation',
        yaxis='y1',
        mode='lines',
        marker={
            'size': 15,
            'line': {'width': 0.5, 'color': 'white'}
        },
    ))

    if sel_plot == 'cost_graph':
        display_data = {
            'data': list(traces[0:2]),
            'layout': go.Layout(
                title='Costs',
                xaxis={'title': 'Years'},
                yaxis={'title': 'Costs [EUR]'},
                legend=dict(x=-.1, y=1.2))
        }
    elif sel_plot == 'power_graph':
        display_data = {
            'data': list(traces[2:5]),
            'layout': go.Layout(
                title='Energy Overview',
                xaxis={'title': 'Time'},
                yaxis={'title': 'Energy [kWh]', 'rangemode': 'tozero'},
                legend=dict(x=-.1, y=1.1, orientation='h'))
        }
    else:
        display_data = {
            'data': list(traces[5]),
            'layout': go.Layout(
                title='Daily Radiation and Consumption',
                xaxis={'title': 'Time'},
                yaxis={'title': 'Radiation [W/m2]', 'range': [0, 1000]},
                legend=dict(x=-.1, y=1.2)
            )
        }

    return display_data
