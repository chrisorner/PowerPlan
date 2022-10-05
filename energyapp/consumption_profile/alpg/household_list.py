from energyapp.consumption_profile.alpg import households


def getHouseholdList(householdType):
    householdList = []

    # Select the types of households
    if householdType == "single_work":
        for i in range(0, 1):
            householdList.append(households.HouseholdSingleWorker())

    elif householdType == "single_retired":
        for i in range(0, 1):
            householdList.append(households.HouseholdSingleRetired())


    elif householdType == "dual_work":
        for i in range(0, 1):
            householdList.append(households.HouseholdDualWorker())

    elif householdType == "dual_retired":
        for i in range(0, 1):
            householdList.append(households.HouseholdDualRetired())

    elif householdType == "fam_dual_work":
        for i in range(0, 1):
            householdList.append(households.HouseholdFamilyDualWorker())

    return householdList
