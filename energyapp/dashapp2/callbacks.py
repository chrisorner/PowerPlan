import os
import datetime
import numpy as np
import pandas as pd
import json
from dash.dependencies import Input, Output, State
from energyapp.dashapp2.models import Solar, Battery, Costs
from energyapp.dashapp2.functions.helper_fnc_data import read_alpg_results
import plotly.graph_objs as go
from energyapp.dashapp2.functions.helper_fnc_calc import get_battery_costs, get_solar_power

startTime = "20180101"
endTime = "20181231"
freq = "H"


# load energy constumption data
consumption_profile = 'energyapp/dashapp1/alpg/output/results/Electricity_Profile_ForOptimization.csv'
if os.path.exists(consumption_profile) and os.stat(consumption_profile).st_size != 0:
    load_elec = read_alpg_results(consumption_profile, "Total", start=startTime, end=endTime, freq=freq)
    load_heat = read_alpg_results(consumption_profile, "HeatDemand", start=startTime, end=endTime, freq=freq)
else:
    load_elec = np.zeros(8760)
    load_heat = np.zeros(8760)


def register_callbacks(dashapp):
    @dashapp.callback(
        Output('store_location', 'children'),
        [Input('button_loc', 'n_clicks')],
        [State('location', 'value')])
    def change_loc(n_clicks, location):
        return location

    @dashapp.callback(
        Output('placeholder_report', 'children'),
        [Input('button_report', 'n_clicks')],
        [State('placeholder_report_url','children')])
        

    @dashapp.callback(

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
        [State('cost_bat', 'value'),
        State('capacity', 'value'),
        State('years', 'value'),
        State('cost_kwh', 'value'),
        State('cost_wp', 'value'),
        State('A_cells', 'value'),
        State('panel_tilt','value'),
        State('panel_orient','value'),
        State('inc_cost_ener','value'),
        State('inflation','value'),
        ],
    )
    def update_cost(module, loc, n_clicks, cost_bat, cap_bat, years_input, cost_kwh, cost_wp,
                    area_cells, tilt, orient, cost_inc, infl):
        ##Update everything with input data
        Temp = 298  # Ambient Temperature
        years_input = int(years_input)

        # Find today's date and end date in 5 days
        #time_vec6d = np.linspace(0, 8580, 24 * 6)
        #today = datetime.datetime.today().strftime('2008-%m-%dT00:00')
        #time_end = datetime.date.today() + datetime.timedelta(days=5)
        #end_time = time_end.strftime('2008-%m-%dT23:00')

        bat_cost = float(cost_bat) * float(cap_bat)

        # Solar Model
        cost_inc= float(cost_inc)
        infl = float(infl)
        area_cells = float(area_cells)
        tilt = float(tilt)
        orient = float(orient)
        sol = Solar()
        _, irrad_global, p_sol = get_solar_power(solar_instance=sol, area=area_cells, tilt= tilt, orient=orient, start=startTime,
                                              end=endTime, freq=freq)

        # Cost Model
        p_peak = area_cells * sol.efficiency * 1000
        bat = Battery()
        bat.calc_soc(cap_bat, load_elec, p_sol)
        e_batt = bat.get_stored_energy()
        e_grid = bat.get_from_grid()
        e_sell = bat.get_w_unused()

        cost = Costs(irrad_global, years_input, cost_kwh, p_peak, cost_inc, infl)
        cost.calc_costs(irrad_global, years_input, bat_cost, p_peak, cost_wp, load_elec, e_grid, e_sell)
        grid_costs = cost.total_costs
        solar_costs = cost.total_costs_sol

        p_cons = load_elec

        costs_with_batteries = get_battery_costs(load_elec, p_sol, irrad_global, years_input, float(cost_bat),
                                                 p_peak, cost_wp, cost_inc, infl, cost_kwh)

        exportJson = False

        if exportJson:
            temp = np.ones(8760)*10
            elec_price_in = np.ones(8760)*0.30
            gas_price = np.ones(8760)*0.07
            elec_price_out= np.ones(8760)*0.11
            ev_aval = np.ones(8760)
            data = np.stack((temp, p_sol,load_heat,load_elec,elec_price_in,gas_price,elec_price_out, ev_aval), axis=1)
            df = pd.DataFrame(data, columns=["temperature", "solar_power", "load_heat", "load_elec", "ele_price_in", "gas_price", "ele_price_out", "ev_aval"])
            df_selected = df.iloc[0:48]
            #df_json = df.to_json(orient="columns")
            df_json = df_selected.to_json(orient="columns")
            with open("data.json", "w") as jsonFile:
                jsonFile.write(df_json)


        return json.dumps(p_sol.tolist()), json.dumps(load_elec.tolist()), json.dumps(irrad_global.tolist()), \
            json.dumps(e_batt.tolist()), json.dumps(e_grid.tolist()), json.dumps(e_sell.tolist()),\
            json.dumps(grid_costs.tolist()), json.dumps(solar_costs.tolist()), json.dumps(costs_with_batteries.tolist())


    @dashapp.callback(

        Output('graph_solpower', 'figure'),
        [Input('store_p_sol', 'children')])

    def solar_power(sol_power_json):

            try:
                sol_power = json.loads(sol_power_json)
            except TypeError:
                sol_power= np.zeros(8785)

            rad_time = list(range(1,8785))
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
    @dashapp.callback(
        Output('graph-batteries', 'figure'),
        #[Input('button_calc', 'n_clicks')],
        [Input('store_cost_with_batteries','children')])

    def batterie_costs(costs_batteries_json):

        if costs_batteries_json:
            batteries_list = json.loads(costs_batteries_json)
            batteries = np.array(batteries_list)
            years = list(range(0, 21))
            trace = []
            for i in range(np.size(batteries,1)):
                trace.append(go.Scatter(
                    x=years,
                    y=batteries[:,i],
                    mode='lines',
                    marker={
                        'size': 5,
                        'line': {'width': 0.5}
                    },
                    name=f'{i+1}kw',
                ))

            return {
                'data': trace,
                'layout': go.Layout(
                    title='Solar Power',
                    xaxis={'title': 'Years'},
                    yaxis=dict(title= 'Costs [EUR]',range=[0,30000]),
                    legend=dict(x=-.1, y=1.2, orientation='h'))
            }

    @dashapp.callback(
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

    def update_graph_costs(sel_plot, years_input, rad_val_json, e_batt_json, e_grid_json, e_sell_json, grid_costs_json,  solar_costs_json):

        traces= []


        try:
            rad_val = json.loads(rad_val_json)
            e_batt = json.loads(e_batt_json)
            e_grid = json.loads(e_grid_json)
            e_sell = json.loads(e_sell_json)
            grid_costs = json.loads(grid_costs_json)
            solar_costs = json.loads(solar_costs_json)
        except TypeError:
            rad_val = np.zeros(8785)
            e_batt = np.zeros(8785)
            e_grid = np.zeros(8785)
            e_sell = np.zeros(8785)
            grid_costs = np.zeros(21)
            solar_costs = np.zeros(21)


        years = int(years_input)

        # rad_time = np.linspace(1, 8760 * years, 8760)
        rad_time = list(range(0, 8785))
    #    t_len = len(rad_val)
    #    d_len = int(t_len / 24)

        # Create Graphs
        traces= []
        traces.append(go.Scatter(
            x=list(range(0, years + 1)),
            y=grid_costs,
            mode='lines',
            name= 'Cost without Solar Panels',
            marker={
                'size': 5,
                'line': {'width': 0.5, 'color': 'blue'}
            }
        ))

        traces.append(go.Scatter(
            x=list(range(0, years + 1)),
            y=solar_costs,
            mode='lines',
            name= 'Cost with Solar Panels',
            marker={
                'size': 5,
                'line': {'width': 0.5, 'color': 'blue'}
            }
        ))
        data= list(traces[0:2])
        layout= go.Layout(
            xaxis={'title': 'Years'},
            yaxis={'title': 'Costs [EUR]'},
            legend=dict(x=-.1, y=1.2),
            plot_bgcolor= 'white')
        fig = go.Figure(data,layout)

        traces.append(go.Scatter(
                x=rad_time[0:119],
                y=e_batt[0:119],
                name='Energy Stored',
                mode='lines',
                marker={
                    'size': 15,
                    'line': {'width': 0.5, 'color': 'white'}
                }
            ))

        traces.append(go.Scatter(
                x=rad_time[0:119],
                y=e_grid[0:119],
                name='Energy Bought',
                mode='lines',
                marker={
                    'size': 15,
                    'line': {'width': 0.5, 'color': 'green'}
                },
            ))

        traces.append(go.Scatter(
            x=rad_time[0:119],
            y=e_sell[0:119],
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

    @dashapp.callback(
        Output('graph_optimize', 'figure'),
        [Input('store_p_sol', 'children')]
    )

    def update_graph_costs(sol_power_json):
        sol_power = [i/1000 for i in json.loads(sol_power_json)]
        df = pd.DataFrame(
            {"solar_power": sol_power,
             "load_elec": load_elec,
             "heat_load": load_heat}
        )

        single_day = df.loc[0:23]

