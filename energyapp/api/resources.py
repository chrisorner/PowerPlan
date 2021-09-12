from flask_restful import Resource, fields, marshal_with
from flask import jsonify
import pandas as pd
from energyapp.dashapp2.models import Solar
from energyapp.dashapp2.functions.helper_fnc_calc import get_solar_power
from energyapp.dashapp2.functions.helper_fnc_data import get_consumption, get_token

token = get_token()
startTime = "20210701"
endTime = "20210702"

class MyDateFormat(fields.Raw):
    def format(self, value):
        return value.strftime("%Y-%m-%d %H:%M:%S")


resource_fields = {
    "ts": MyDateFormat,
    "val": fields.String
}


class SolarPower(Resource):
    @marshal_with(resource_fields)
    def get(self):
        sol = Solar()
        area_cells = 20
        tilt = 30
        orient = 180
        freq = "min"
        time, _, p_sol = get_solar_power(solar_instance=sol, area=area_cells, tilt=tilt, orient=orient, start=startTime,
                                         end=endTime, freq=freq)
        # solarData = pd.DataFrame({"time": time, "power": p_sol}, index="time")
        # consumptionData = pd.DataFrame(get_consumption(token, start=startTime, end=endTime))
        return [dict([("ts", ts), ("val", val)]) for ts, val in zip(time, p_sol)]


class Consumption(Resource):
    def get(self):
        data = get_consumption(token, start=startTime, end=endTime)
        return jsonify(data)