# Artifical load profile generator v1.2, generation of artificial load profiles to benchmark demand side management approaches
# Copyright (C) 2018 Gerwin Hoogsteen

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import random

from energyapp.consumption_profile.alpg import profilegentools
from energyapp.consumption_profile.alpg.configs import external_inputs


class House:
    # In the end we need to define houses as well with their orientation
    def __init__(self):
        self.hasPV = False
        self.hasBattery = False

    def addPV(self, area):
        self.hasPV = True
        self.pvArea = area
        self.pvEfficiency = random.randint(external_inputs.PVEfficiencyMin, external_inputs.PVEfficiencyMax)
        self.pvAzimuth = profilegentools.gaussMinMax(external_inputs.PVAzimuthMean, external_inputs.PVAzimuthSigma)
        if (self.pvAzimuth < 0):
            self.pvAzimuth = self.pvAzimuth + 360
        self.pvElevation = profilegentools.gaussMinMax(external_inputs.PVAngleMean, external_inputs.PVAngleSigma)

    def addBattery(self, capacity, power):
        if capacity > 0:
            self.hasBattery = True
            self.batteryCapacity = capacity
            self.batteryPower = power
