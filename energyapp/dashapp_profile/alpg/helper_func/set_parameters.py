import os
#alpg_folder = os.path.dirname(os.path.abspath(__file__))
#config_file = os.path.join(alpg_folder, 'configs/external_inputs.py')
from energyapp.dashapp_profile.alpg.configLoader import cfgFile


def set_parameters(numKids, yearly_cons, dist, householdType):

    with open(cfgFile, 'r') as file:
        data = file.readlines()

    data[143] = 'numKids = ' + str(numKids) + '\n'
    data[144] = 'yearlyConsumption = ' + str(yearly_cons) + '\n'
    data[145] = 'distancetoWork = ' + str(dist) + '\n'
    data[146] = f'householdType = "{householdType}" \n'

    with open(cfgFile, 'w') as file:
        file.writelines(data)