# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 06:24:43 2019

@author: chris
"""

import numpy as np
import requests
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
# finally, we import the pvlib library
import pvlib
from pvlib import pvsystem
from pvlib.temperature import sapm_cell, TEMPERATURE_MODEL_PARAMETERS
#from pvlib.forecast import GFS, NAM, NDFD, HRRR, RAP

#np.set_printoptions(threshold=np.nan)
#from scipy.optimize import fsolve


#class Solar:

#    def __init__(self, rad):
#        t_ges = len(rad)
#        self.P_solar = np.zeros(t_ges)

#    def calc_power(self, rad, area, cell):
#        efficiency = cell.efficiency
#        self.P_solar = [i*area*efficiency/100 for i in rad]
#        return self.P_solar


class Solar2:

    def __init__(self):

        self.latitude = 48.8566101
        self.longitude = 2.3514992
        self.tz= 'CET'
        self.surface_tilt = 30
        self.surface_azimuth = 180
        self.sun_zen = 0
        self.air_mass = 0
        self.area = 0
        self.efficiency = 0

    def get_location(self, city):
        geolocator = Nominatim(user_agent="Enefso")
        try:
            location = geolocator.geocode(city)
            self.longitude = location.longitude
            self.latitude = location.latitude
        except GeocoderTimedOut:
            self.longitude = 2.3514992
            self.latitude = 48.8566101



 #   def forecast(self, lat, long, start, end):
 #       fm = GFS()
 #       forecast_data = fm.get_processed_data(lat, long, start, end)
 #       return forecast_data

    def calc_irrad(self, times, lat, lon, tz, city):
        tus= pvlib.location.Location(lat, lon, tz=tz, altitude=0, name=city)
        ephem_data = tus.get_solarposition(times)
        irrad_data = tus.get_clearsky(times)
        irrad_data.to_csv('irrad_data',index= False)
        self.sun_zen = ephem_data['apparent_zenith']
        self.air_mass = pvlib.atmosphere.get_relative_airmass(self.sun_zen)
        dni_et = pvlib.irradiance.get_extra_radiation(times.dayofyear)
        

        total = pvlib.irradiance.get_total_irradiance(
            self.surface_tilt, self.surface_azimuth,
            ephem_data['apparent_zenith'], ephem_data['azimuth'],
            dni=irrad_data['dni'], ghi=irrad_data['ghi'], dhi=irrad_data['dhi'],
            dni_extra=dni_et, airmass=self.air_mass,
            model='isotropic',
            surface_type='urban')

        return total

    def pv_system(self,times, irrad, module, cell_area):

        wind= pd.Series(5,index= times)
        temp= pd.Series(20, index= times)
        pressure= 101325
        airmass = self.air_mass
        am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
        solpos = pvlib.solarposition.get_solarposition(times, self.latitude, self.longitude)
        #pvtemp = pvsystem.sapm_celltemp(irrad['poa_global'], wind, temp)
        params = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
        pvtemp = sapm_cell(irrad['poa_global'], wind, temp, **params)

        sandia_modules = pvsystem.retrieve_sam(name='SandiaMod')
        sandia_module = sandia_modules[module]
        self.area= sandia_module.loc['Area']
        I_mp = sandia_module.loc['Impo']
        V_mp = sandia_module.loc['Vmpo']
        self.efficiency = (I_mp*V_mp)/(self.area*1000)
        #sandia_module= module
        #module_names = list(sandia_modules.columns)

        aoi = pvlib.irradiance.aoi(self.surface_tilt, self.surface_azimuth,
                                   solpos['apparent_zenith'], solpos['azimuth'])

        effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(
            irrad['poa_direct'], irrad['poa_diffuse'],
            am_abs, aoi, sandia_module)
        module_power = pvlib.pvsystem.sapm(effective_irradiance, pvtemp, sandia_module)
        total_power = module_power['p_mp']/self.area*cell_area

        return total_power.values


class Battery:

    def __init__(self):
        t_ges = 8760 + 1
        # maximum storage capacity in Wh
        # Wmax only initialized, input from gui
        self.w_max = 100
        self.stored_energy = np.zeros(t_ges)
        self.SOC = np.zeros(t_ges)
        self.from_grid = np.zeros(t_ges) # Power drawn from grid
        self.W_unused = np.zeros(t_ges) # Power that is fed into grid
        self.p_store = np.zeros(t_ges) # Power that goes into battery

    def get_soc(self):
        return self.SOC

    def get_w_unused(self):
        # Energy which is not used or stored
        x = self.W_unused
        return x

    def get_stored_energy(self):
        x = self.stored_energy
        return x

    def get_from_grid(self):
        x = self.from_grid
        return x

    def calc_soc(self, bat_capacity, cons_ener, p_mpp):
        t_len = int(len(p_mpp))
        # Wmax input from GUI
        self.w_max = int(bat_capacity)

        for i in range(np.size(cons_ener)):
            self.p_store[i] = p_mpp[i] / 1000 - cons_ener[i]

        for i in range(t_len):
            # battery is neither full nor empty and can be charged/discharged
            if (self.stored_energy[i - 1] + self.p_store[i] >= 0) and (
                    self.stored_energy[i - 1] + self.p_store[i] <= self.w_max):  # charge
                # Pmpp from solargen
                self.stored_energy[i] = self.stored_energy[i-1] + self.p_store[i]
                self.W_unused[i] = 0

            # battery empty and cannot be discharged
            elif self.stored_energy[i - 1] + self.p_store[i] < 0:
                self.stored_energy[i] = 0
                self.W_unused[i] = 0
                self.from_grid[i] = abs(self.p_store[i])
                # print(i)

            # battery full and cannot be charged
            elif self.stored_energy[i - 1] + self.p_store[i] > self.w_max:
                # print(self.Wmax-self.stored_energy[i-1])
                self.W_unused[i] = self.stored_energy[
                    i - 1] + self.p_store[i] - self.w_max
                self.stored_energy[i] = self.w_max

            self.SOC[i] = self.stored_energy[i] / self.w_max


class Costs:
    def __init__(self, rad, inp_years, cost_kwh, power, cost_inc, infl):
        self.t_len = int(len(rad))
        if len(rad) < 145:
            time_frame = self.t_len
        else:
            time_frame = inp_years

        self.cost_energy_inc = cost_inc
        self.cost_basic = 100
        self.cost_kwh = float(cost_kwh)
        years = np.arange(inp_years)
        self.cost_var = self.cost_kwh * (1 + self.cost_energy_inc) ** years  # variable cost for energy
        self.cost_fix = power # Fix costs
        cost_dep = 5 * power / 1000 # cost depending on power consumption
        # Operational costs incl repair
        self.cost_operate = self.cost_fix + cost_dep
        self.inflation= infl
        self.feedInTariff = 0.1147 #€/kwh

        self.cons_year = np.zeros(self.t_len + 1)  # index 0 is always 0, costs start at index 1
        self.total_costs = np.zeros(time_frame + 1)
        self.total_costs_sol = np.zeros(time_frame + 1)
        self.cons_sol_year = np.zeros(self.t_len+1)
        self.feedIn_year = np.zeros(self.t_len+1)

    @property
    def cost_fix(self):
        return self.__cost_fix

    @cost_fix.setter
    def cost_fix(self, power):
        # Operational costs incl repair. For solar system above 8kW additional 21€/a for production counter is required
        if power/1000 > 8:
            self.__cost_fix = 148+21
        else:
            self.__cost_fix = 148


    def battery_invest(self, capacity, cost_per_kwh):
        invest = float(cost_per_kwh) * float(capacity)
        return invest

    def solar_invest(self, power, cost_per_kwp):
        # solar power in W but price per kwp
        # 𝐼𝑛𝑣𝑒𝑠𝑡𝑚𝑒𝑛𝑡 𝑐𝑜𝑠𝑡𝑠:𝑃𝑎𝑛𝑒𝑙𝑠, 𝐶𝑜𝑢𝑛𝑡𝑒𝑟, 𝑖𝑛𝑠𝑡𝑎𝑙𝑙𝑎𝑡𝑖𝑜𝑛, 𝑝𝑜𝑤𝑒𝑟 𝑒𝑙𝑒𝑐𝑡𝑟𝑜𝑛𝑖𝑐𝑠 (Average Germany)
        p_kw = (float(power) / 1000)
        invest_per_kw= float(cost_per_kwp)

        invest = p_kw**(-0.16) * p_kw * invest_per_kw * (1+0.19)
        return invest

    def calc_costs(self, rad, inp_years, cost_bat, power, cost_per_kwp, cons_ener, pow_from_grid, pow_sell):
        # cost calculated for 6 days without investmetn  costs using global d_len
        #cost_battery = self.battery_invest(capacity, cost_bat)
        cost_battery = cost_bat
        cost_solar = self.solar_invest(power, cost_per_kwp)

        p_cons = cons_ener  # power req by consumer

        if len(rad) < 145:  # indicates forecast, then without investment
            for i in range(self.t_len):
                cost_grid = self.cost_kwh * pow_from_grid
                # index 0 is 0
                self.total_costs[i + 1] = p_cons[i]*self.cost_kwh
                self.total_costs_sol[i + 1] = self.total_costs_sol[
                                              i] + cost_grid[i]  # for short-term prediction without investment costs
        else:
            self.total_costs_sol[0] = cost_solar + cost_battery


            # calc the costs for the energy required from the grid (with solar panels)
            for i in range(self.t_len):


                # calc the daily costs without solar panels (1 year)
                self.cons_year[i + 1] = self.cons_year[i] + p_cons[i]
                # calc the daily costs with solar panels (1 year)
                self.cons_sol_year[i + 1] = self.cons_sol_year[i]+pow_from_grid[i]
                self.feedIn_year[i + 1] = self.feedIn_year[i] + pow_sell[i]


            # calculate the slope of the cost function with and without solar panels
            slope1 = self.cons_year[-1] / 365
            slope = self.cons_sol_year[-1]/365
            slope2 = self.feedIn_year[-1]/365
            for i in range(inp_years):
                # extrapolate the costs over the desired number of years
                # Barwertmethode
                self.total_costs[i+1] = self.total_costs[i]+(slope1*365*self.cost_var[i] +
                                                             self.cost_basic)*(1+self.inflation)**(-(i+1))
                self.total_costs_sol[i+1] = self.total_costs_sol[i]+(slope*365*self.cost_var[i] +
                                                self.cost_operate + self.cost_basic - slope2*365*self.feedInTariff) * \
                                                (1+self.inflation)**(-(i+1))


if __name__ == "__main__":
    import os
    from energyapp.dashapp2.models import Solar2, Battery, Costs
    from energyapp.dashapp2.functions.helper_fnc_data import read_alpg_results
    from energyapp.dashapp2.functions.compareBattery import get_battery_costs

    years_input = 20
    spec_cost_bat = 1500 #per kWh
    cap_bat = 5 #kWh

    bat_cost = spec_cost_bat * cap_bat

    # if n_clicks:

    # Solar Model
    cost_inc = 0.01 #yearly increase of energy costs
    infl = 0.02 #yearly inflation
    area_cells = 50
    tilt = 30
    orient = 180
    loc = "Berlin"
    all_modules = pvsystem.retrieve_sam(name='SandiaMod')
    module_names = list(all_modules.columns)
    module = module_names[124]

    sol2 = Solar2()
    sol2.surface_tilt = tilt
    sol2.surface_azimuth = orient
    sol2.get_location(loc)
    times = pd.date_range(start='1/1/2020', end='2020/12/31', freq='H', tz=sol2.tz)
    times = times[:-1]
    irradiation = sol2.calc_irrad(times, sol2.latitude, sol2.longitude, sol2.tz, loc)
    irrad_global = irradiation['poa_global']
    p_sol = sol2.pv_system(times, irradiation, module, area_cells)

    # Battery model
    base_dir = os.path.abspath(os.getcwd())
    input_file = r'../dashapp1/alpg/output/results/Electricity_Profile.csv'
    consumption = read_alpg_results(input_file)

    p_peak = area_cells * sol2.efficiency * 1000
    bat = Battery()
    bat1 = Battery()
    bat.calc_soc(cap_bat, consumption, p_sol)
    e_batt = bat.get_stored_energy()
    e_grid = bat.get_from_grid()
    e_sell = bat.get_w_unused()


    # Cost model
    cost_kwh = 0.3 # 0.3 Eur/kwh
    cost_wp = 1200 #Eur/kWp

    cost = Costs(irrad_global, years_input, cost_kwh, p_peak, cost_inc, infl)
    cost1 = Costs(irrad_global, years_input, cost_kwh, p_peak, cost_inc, infl)
    cost.calc_costs(irrad_global, years_input, bat_cost, p_peak, cost_wp, consumption, e_grid, e_sell)
    grid_costs = cost.total_costs
    solar_costs = cost.total_costs_sol

    p_cons = consumption
    irrad_array = irrad_global.values

    costs_with_batteries = get_battery_costs(consumption, p_sol, irrad_global, years_input, float(spec_cost_bat), p_peak,
                                             cost_wp, cost1, bat1)
