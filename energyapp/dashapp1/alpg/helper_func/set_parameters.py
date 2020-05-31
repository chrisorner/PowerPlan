import os
#alpg_folder = os.path.dirname(os.path.abspath(__file__))
#config_file = os.path.join(alpg_folder, 'configs/external_inputs.py')
from energyapp.dashapp1.alpg.configLoader import cfgFile


def set_parameters(numKids, yearly_cons, dist):

    with open(cfgFile, 'r') as file:
        data = file.readlines()

    data[143] = 'numKids = ' + str(numKids) + '\n'
    data[144] = 'yearlyConsumption = ' + str(yearly_cons) + '\n'
    data[145] = 'distancetoWork = ' + str(dist) + '\n'


    with open(cfgFile, 'w') as file:
        file.writelines(data)