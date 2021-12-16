import pandas as pd
import numpy as np
from energyapp.dashapp_simulation.models import Solar, Battery, Costs


def get_solar_power(solar_instance, area, tilt, orient, start='20200101', end='20200102', freq="H",
                    module='Canadian_Solar_CS5P_220M___2009_', loc = "Berlin"):
    area_cells = area
    tilt = tilt
    orient = orient
    module = module
    loc = loc
    solar_instance.surface_tilt = tilt
    solar_instance.surface_azimuth = orient
    solar_instance.get_location(loc)
    # pd.offset to make end date inclusive, tz must be UTC because weather data is UTC
    times = pd.date_range(start=start, end=pd.to_datetime(end) + pd.offsets.Day(), freq=freq, tz="UTC")
    # Don't send the last time which is 0:00 of next day
    times = times[:-1]
    irradiation, weather, am_abs, aoi = solar_instance.calc_irrad(times, solar_instance.latitude, solar_instance.longitude, solar_instance.tz, loc)
    irrad_global = irradiation['poa_global']
    p_sol = solar_instance.pv_system(irradiation, weather, am_abs, aoi, module, area_cells)
    if "min" in freq:
        # if freq is in minutes then upsample and use linear interpolation. Else sum the values for downsampling
        irrad_global_resampled = irrad_global.resample(freq).interpolate(method='linear')
        p_sol_resampled = p_sol.resample(freq).interpolate(method='linear')
    else:
        irrad_global_resampled = irrad_global.resample(freq).mean()
        p_sol_resampled = p_sol.resample(freq).mean()
    irrad_global_resampled = irrad_global_resampled[times[0]:times[-1]]
    p_sol_resampled = p_sol_resampled[times[0]:times[-1]]

    return times, irrad_global_resampled.values, p_sol_resampled.values


def get_battery_costs(consumption, p_sol, irrad_global, years_input, bat_cost_kw, p_peak, cost_wp, cost_inc, infl,
                          cost_kwh):
    capacities = np.linspace(1, 10, 10)
    total_costs = np.zeros((21, len(capacities)))

    for i in range(len(capacities)):
        bat = Battery()
        cost_battery = capacities[i] * bat_cost_kw
        bat.calc_soc(capacities[i], consumption, p_sol)
        e_grid = bat.get_from_grid()
        e_sell = bat.get_w_unused()
        cost = Costs(irrad_global, years_input, cost_kwh, p_peak, cost_inc, infl)
        cost.calc_costs(irrad_global, years_input, cost_battery, p_peak, cost_wp, consumption, e_grid, e_sell)
        total_costs[:, i] = cost.total_costs_sol

    return total_costs

if __name__ == "__main__":
    power = get_solar_power()