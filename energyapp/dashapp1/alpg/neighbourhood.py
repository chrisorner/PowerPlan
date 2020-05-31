
	#Artifical load profile generator v1.2, generation of artificial load profiles to benchmark demand side management approaches
    #Copyright (C) 2018 Gerwin Hoogsteen

    #This program is free software: you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation, either version 3 of the License, or
    #(at your option) any later version.

    #This program is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.

    #You should have received a copy of the GNU General Public License
    #along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys, random
print(sys.path)
from energyapp.dashapp1.alpg.configs import external_inputs
from energyapp.dashapp1.alpg.household_list import householdList

from energyapp.dashapp1.alpg import houses

class neighbourhood:
	houseList = []
	pvList = [0] * len(householdList)
	batteryList = [0] * len(householdList)
	inductioncookingList = [0] * len(householdList)

	for i in range(0, len(householdList)):
		houseList.append(houses.House())
	
	#Add PV to houses:
	for i in range(0, len(householdList)):
		if i < (round(len(householdList)*(external_inputs.penetrationPV/100))):
			pvList[i] = 1
	
	#And randomize:
	random.shuffle(pvList)

	#Add induction cooking
	for i in range(0, len(householdList)):
		if i < (round(len(householdList)*(external_inputs.penetrationInductioncooking/100))):
			inductioncookingList[i] = 1
	random.shuffle(inductioncookingList)
	for i in range(0, len(householdList)):
		if inductioncookingList[i] == 1:
			householdList[i].hasInductionCooking = True
	
	# Add Combined Heat Power
	i = 0
	while i < (round(len(householdList)*(external_inputs.penetrationCHP/100))) - (round(len(householdList)*(external_inputs.penetrationPV/100))):
		j = random.randint(0,len(householdList)-1)
		if householdList[j].hasCHP == False and pvList[j] == 0: # First supply houses without PV
			householdList[j].hasCHP = True
			i = i + 1
	if (round(len(householdList)*(external_inputs.penetrationPV/100))) > (round(len(householdList)*(external_inputs.penetrationCHP/100))): # If there are too much CHPs compared to PV, add some more CHPS
		while i < (round(len(householdList)*(external_inputs.penetrationCHP/100))):
			j = random.randint(0,len(householdList)-1)
			if householdList[j].hasCHP == False: # First supply houses without PV
				householdList[j].hasCHP = True
				i = i + 1
			
	# Add heat pumps
	i = 0
	while i < (round(len(householdList)*(external_inputs.penetrationHeatPump/100))):
		j = random.randint(0,len(householdList)-1)
		if householdList[j].hasHP == False and householdList[j].hasCHP == False:
			householdList[j].hasHP = True
			i = i + 1

	#Now add batteries
	i = 0
	while i < (round(len(householdList)*(external_inputs.penetrationBattery/100))):
		j = random.randint(0,len(householdList)-1)
		if (pvList[j] == 1 or householdList[j].hasCHP) and batteryList[j] == 0:
			batteryList[j] = 1
			i = i + 1
	
	# Add EVs
	drivingDistance = [0] * len(householdList)
	for i in range(0, len(householdList)):
		drivingDistance[i] = householdList[i].Persons[0].DistanceToWork
		drivingDistance = sorted(drivingDistance, reverse=True)
	for i in range(0, len(drivingDistance)):
		if i < (round(len(householdList)*(external_inputs.penetrationEV/100))+round(len(householdList)*(external_inputs.penetrationPHEV/100))):
			#We can still add an EV
			added = False
			j = 0
			while added == False:
				if householdList[j].Persons[0].DistanceToWork == drivingDistance[i]:
					if householdList[j].hasEV == False:
						if i < (round(len(householdList)*(external_inputs.penetrationEV/100))):
							householdList[j].Devices["ElectricalVehicle"].BufferCapacity = external_inputs.capacityEV
							householdList[j].Devices["ElectricalVehicle"].Consumption = external_inputs.powerEV
						else:
							householdList[j].Devices["ElectricalVehicle"].BufferCapacity = external_inputs.capacityPHEV
							householdList[j].Devices["ElectricalVehicle"].Consumption = external_inputs.powerPHEV
						householdList[j].hasEV = True
						added = True
				j = j + 1
	
	#Shuffle
	random.shuffle(householdList)
		
	#And then map households to houses
	for i in range(0,len(householdList)):
		householdList[i].setHouse(houseList[i])
		#add solar panels according to the size of the annual consumption:
		if pvList[i] == 1:
			# Do something fancy
			# A solar panel will produce approx 875kWh per kWp on annual basis in the Netherlands:
			# https://www.consumentenbond.nl/energie/extra/wat-zijn-zonnepanelen/
			# Furthermore, the size of a single solar panel is somewhere around 1.6m2 (various sources)
			# Hence, if a household is to be more or less energy neutral we have:
			area = round( (householdList[i].ConsumptionYearly / external_inputs.PVProductionPerYear) * 1.6) #average panel is 1.6m2
			householdList[i].House.addPV(area)
			
		if batteryList[i] == 1:
			# Do something based on the household size and whether the house has an EV:
			if householdList[i].hasEV:
				#House has an EV as well!
				householdList[i].House.addBattery(external_inputs.capacityBatteryLarge, external_inputs.powerBatteryLarge) #Let's give it a nice battery!
			else:
				#NO EV, just some peak shaving:
				if(householdList[i].ConsumptionYearly > 2500):
					householdList[i].House.addBattery(external_inputs.capacityBatteryMedium, external_inputs.powerBatteryMedium)
				else:
					householdList[i].House.addBattery(external_inputs.capacityBatterySmall, external_inputs.powerBatterySmall)
