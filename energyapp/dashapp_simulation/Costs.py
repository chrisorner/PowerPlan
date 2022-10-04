import numpy as np

from energyapp.dashapp_simulation.Battery import Battery


class Costs:
    def __init__(self, irrad_global, years_input, cost_kwh, power, cost_el_increase, inflation):
        self.t_len = int(len(irrad_global))
        if len(irrad_global) < 145:
            time_frame = self.t_len
        else:
            time_frame = years_input

        self.cost_energy_inc = cost_el_increase
        self.cost_basic = 100
        self.cost_kwh = float(cost_kwh)
        years = np.arange(years_input)
        self.cost_var = self.cost_kwh * (1 + self.cost_energy_inc) ** years  # variable cost for energy
        self.cost_fix = power  # Fix costs
        cost_dep = 5 * power / 1000  # cost depending on power consumption
        # Operational costs incl repair
        self.cost_operate = self.cost_fix + cost_dep
        self.inflation = inflation
        self.feedInTariff = 0.1147  # €/kwh

        self.cons_year = np.zeros(self.t_len + 1)  # index 0 is always 0, costs start at index 1
        self.total_costs = np.zeros(time_frame + 1)
        self.total_costs_sol = np.zeros(time_frame + 1)
        self.cons_sol_year = np.zeros(self.t_len + 1)
        self.feedIn_year = np.zeros(self.t_len + 1)

    @property
    def cost_fix(self):
        return self._cost_fix

    @cost_fix.setter
    def cost_fix(self, power):
        # Operational costs incl repair. For solar system above 8kW additional 21€/a for production counter is required
        if power / 1000 > 8:
            self._cost_fix = 148 + 21
        else:
            self._cost_fix = 148

    def battery_invest(self, capacity, cost_per_kwh):
        invest = float(cost_per_kwh) * float(capacity)
        return invest

    def solar_invest(self, power, cost_solar_panel):
        # solar power in W but price per kwp
        # 𝐼𝑛𝑣𝑒𝑠𝑡𝑚𝑒𝑛𝑡 𝑐𝑜𝑠𝑡𝑠:𝑃𝑎𝑛𝑒𝑙𝑠, 𝐶𝑜𝑢𝑛𝑡𝑒𝑟, 𝑖𝑛𝑠𝑡𝑎𝑙𝑙𝑎𝑡𝑖𝑜𝑛, 𝑝𝑜𝑤𝑒𝑟 𝑒𝑙𝑒𝑐𝑡𝑟𝑜𝑛𝑖𝑐𝑠 (Average Germany)
        p_kw = (float(power) / 1000)
        invest_per_kw = float(cost_solar_panel)

        invest = p_kw ** (-0.16) * p_kw * invest_per_kw * (1 + 0.19)
        return invest

    def calc_costs(self, irrad_global, years_input, cost_battery, P_solar_peak, cost_solar_panel, P_cons_el, P_grid,
                   P_sell):
        # cost calculated for 6 days without investmetn  costs using global d_len
        # cost_battery = self.battery_invest(capacity, cost_battery)
        cost_battery = cost_battery
        cost_solar = self.solar_invest(P_solar_peak, cost_solar_panel)

        if len(irrad_global) < 145:  # indicates forecast, then without investment
            for i in range(self.t_len):
                cost_grid = self.cost_kwh * P_grid
                # index 0 is 0
                self.total_costs[i + 1] = P_cons_el[i] * self.cost_kwh
                self.total_costs_sol[i + 1] = self.total_costs_sol[
                                                  i] + cost_grid[
                                                  i]  # for short-term prediction without investment costs
        else:
            self.total_costs_sol[0] = cost_solar + cost_battery

            # calc the costs for the energy required from the grid (with solar panels)
            for i in range(self.t_len):
                # calc the daily costs without solar panels (1 year)
                self.cons_year[i + 1] = self.cons_year[i] + P_cons_el[i]
                # calc the daily costs with solar panels (1 year)
                self.cons_sol_year[i + 1] = self.cons_sol_year[i] + P_grid[i]
                self.feedIn_year[i + 1] = self.feedIn_year[i] + P_sell[i]

            # calculate the slope of the cost function with and without solar panels
            slope1 = self.cons_year[-1] / 365
            slope = self.cons_sol_year[-1] / 365
            slope2 = self.feedIn_year[-1] / 365
            for i in range(years_input):
                # extrapolate the costs over the desired number of years
                # Barwertmethode
                self.total_costs[i + 1] = self.total_costs[i] + (slope1 * 365 * self.cost_var[i] +
                                                                 self.cost_basic) * (1 + self.inflation) ** (-(i + 1))
                self.total_costs_sol[i + 1] = self.total_costs_sol[i] + (slope * 365 * self.cost_var[i] +
                                                                         self.cost_operate + self.cost_basic - slope2 * 365 * self.feedInTariff) * \
                                              (1 + self.inflation) ** (-(i + 1))

    def compare_battery_costs(self, P_cons, P_sol, irrad_global, years_input, cost_battery_specific, P_sol_peak,
                              cost_wp):
        capacities = np.linspace(1, 10, 10)
        total_costs = np.zeros((21, len(capacities)))

        for i in range(len(capacities)):
            battery = Battery(capacities[i])
            cost_battery = capacities[i] * cost_battery_specific
            battery.calc_soc(P_cons, P_sol)
            P_grid = battery.get_from_grid()
            P_sell = battery.get_w_unused()
            self.calc_costs(irrad_global, years_input, cost_battery, P_sol_peak, cost_wp, P_cons, P_grid, P_sell)
            total_costs[:, i] = self.total_costs_sol

        return total_costs
