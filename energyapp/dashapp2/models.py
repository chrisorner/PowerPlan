# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 06:24:43 2019

@author: chris
"""

import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
# finally, we import the pvlib library
import pvlib

class Solar:

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
        try:
            geolocator = Nominatim(user_agent="Enefso")
            location = geolocator.geocode(city)
            self.longitude = location.longitude
            self.latitude = location.latitude
        except GeocoderTimedOut or GeocoderUnavailable:
            self.longitude = 2.3514992
            self.latitude = 48.8566101
            print("Can't connect to geolocator")



 #   def forecast(self, lat, long, start, end):
 #       fm = GFS()
 #       forecast_data = fm.get_processed_data(lat, long, start, end)
 #       return forecast_data

    def calc_irrad(self, times, lat, lon, tz, city):
        altitude = 20
        location = pvlib.location.Location(lat, lon, tz=tz, altitude=altitude, name=city)
        weather = pvlib.iotools.get_pvgis_tmy(lat, lon, map_variables=True)[0]
        weather.index.name = "time"
        # Change the year of TMY to match the year defined by the user
        weather.reset_index(inplace=True)
        weather["time"] = weather["time"].apply(lambda x: x.replace(year=times.year[0]))
        weather.set_index("time", inplace=True)
        solpos = pvlib.solarposition.get_solarposition(
            time=weather.index,
            latitude=lat,
            longitude=lon,
            altitude=altitude,
            temperature=weather["temp_air"],
            pressure=pvlib.atmosphere.alt2pres(altitude),
                )
        dni_extra = pvlib.irradiance.get_extra_radiation(weather.index)
        self.air_mass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
        pressure = pvlib.atmosphere.alt2pres(altitude)
        am_abs = pvlib.atmosphere.get_absolute_airmass(self.air_mass, pressure)
        aoi = pvlib.irradiance.aoi(
            self.surface_tilt,
            self.surface_azimuth,
            solpos["apparent_zenith"],
            solpos["azimuth"],
        )
        total_irradiance = pvlib.irradiance.get_total_irradiance(
            self.surface_tilt,
            self.surface_azimuth,
            solpos['apparent_zenith'],
            solpos['azimuth'],
            weather['dni'],
            weather['ghi'],
            weather['dhi'],
            dni_extra=dni_extra,
            model='isotropic',
            surface_type='urban'
        )

        return total_irradiance, weather, am_abs, aoi

    def pv_system(self, irrad, weather, am_abs, aoi, module, cell_area):

        sandia_modules = pvlib.pvsystem.retrieve_sam(name='SandiaMod')
        sandia_module = sandia_modules[module]
        temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
        cell_temperature = pvlib.temperature.sapm_cell(
            irrad['poa_global'],
            weather["temp_air"],
            weather["wind_speed"],
            **temperature_model_parameters,
        )
        effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(
            irrad['poa_direct'],
            irrad['poa_diffuse'],
            am_abs,
            aoi,
            sandia_module,
        )

        dc = pvlib.pvsystem.sapm(effective_irradiance, cell_temperature, sandia_module)

        self.area= sandia_module.loc['Area']
        I_mp = sandia_module.loc['Impo']
        V_mp = sandia_module.loc['Vmpo']
        self.efficiency = (I_mp*V_mp)/(self.area*1000)
        #sandia_module= module
        #module_names = list(sandia_modules.columns)

        total_power = dc['p_mp']/self.area*cell_area

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

