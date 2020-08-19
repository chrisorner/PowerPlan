import numpy as np

def get_battery_costs(consumption, p_sol, irrad_global, years_input, bat_cost_kw, p_peak, cost_wp, cost, battery):
    capacities = np.linspace(1,10,10)
    total_costs =  np.zeros((21,len(capacities)))


    for i in range(len(capacities)):
        cost_battery = capacities[i] * bat_cost_kw
        battery.calc_soc(capacities[i], consumption, p_sol)
        e_grid = battery.get_from_grid()
        e_sell = battery.get_w_unused()
        cost.calc_costs(irrad_global, years_input, cost_battery, p_peak, cost_wp, consumption, e_grid, e_sell)
        total_costs[:,i] = cost.total_costs_sol

    return total_costs
