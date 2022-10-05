import numpy as np


class Battery:

    def __init__(self, capacity):
        t_ges = 8760 + 1
        # maximum storage capacity in Wh
        # Wmax only initialized, input from gui
        self.capacity = capacity
        self.stored_energy = np.zeros(t_ges)
        self.SOC = np.zeros(t_ges)
        self.P_grid = np.zeros(t_ges)  # Power drawn from grid
        self.P_unused = np.zeros(t_ges)  # Power that is fed into grid
        self.P_store = np.zeros(t_ges)  # Power that goes into battery

    def get_soc(self):
        return self.SOC

    def get_w_unused(self):
        # Energy which is not used or stored
        x = self.P_unused
        return x

    def get_stored_energy(self):
        x = self.stored_energy
        return x

    def get_from_grid(self):
        x = self.P_grid
        return x

    def calc_soc(self, cons_ener, p_mpp):
        t_len = int(len(p_mpp))

        for i in range(np.size(cons_ener)):
            self.P_store[i] = p_mpp[i] / 1000 - cons_ener[i]

        for i in range(t_len):
            # battery is neither full nor empty and can be charged/discharged
            if (self.stored_energy[i - 1] + self.P_store[i] >= 0) and (
                    self.stored_energy[i - 1] + self.P_store[i] <= self.capacity):  # charge
                # Pmpp from solargen
                self.stored_energy[i] = self.stored_energy[i - 1] + self.P_store[i]
                self.P_unused[i] = 0

            # battery empty and cannot be discharged
            elif self.stored_energy[i - 1] + self.P_store[i] < 0:
                self.stored_energy[i] = 0
                self.P_unused[i] = 0
                self.P_grid[i] = abs(self.P_store[i])
                # print(i)

            # battery full and cannot be charged
            elif self.stored_energy[i - 1] + self.P_store[i] > self.capacity:
                # print(self.Wmax-self.stored_energy[i-1])
                self.P_unused[i] = self.stored_energy[
                                       i - 1] + self.P_store[i] - self.capacity
                self.stored_energy[i] = self.capacity

            self.SOC[i] = self.stored_energy[i] / self.capacity
