from energyapp.dashapp1.alpg import households

householdList = []

#Select the types of households

for i in range(0,0):
	householdList.append(households.HouseholdSingleWorker())

for i in range(0,0):
	householdList.append(households.HouseholdSingleRetired())

for i in range(0,0):
	householdList.append(households.HouseholdDualWorker(True))

for i in range(0,0):
	householdList.append(households.HouseholdDualWorker(False))

for i in range(0,0):
	householdList.append(households.HouseholdDualRetired())

for i in range(0,0):
	householdList.append(households.HouseholdFamilyDualWorker(True))

for i in range(0,1):
	householdList.append(households.HouseholdFamilyDualWorker(False))