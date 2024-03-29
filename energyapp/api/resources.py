from flask import jsonify
from flask_restful import reqparse, Resource, fields, marshal_with

from energyapp.system_simulation.Solar import Solar
from energyapp.utils.helper import get_measured_consumption, get_token

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

parser = reqparse.RequestParser()
parser.add_argument('area')
parser.add_argument('tilt')
parser.add_argument('orient')
parser.add_argument('location')
parser.add_argument('start_time')
parser.add_argument('end_time')
parser.add_argument('freq')


class SolarPower(Resource):
    @marshal_with(resource_fields)
    def post(self):
        args = parser.parse_args()
        sol = Solar()
        area_cells = float(args["area"])
        tilt = float(args["tilt"])
        orient = float(args["orient"])
        start_time = args["start_time"]
        end_time = args["end_time"]
        freq = args["freq"]
        location = args["location"]
        time, _, p_sol = get_solar_power(solar_instance=sol, cell_area=area_cells, tilt=tilt, orient=orient,
                                         start=start_time,
                                         end=end_time, freq=freq, loc=location)
        # solarData = pd.DataFrame({"time": time, "power": p_sol}, index="time")
        # consumptionData = pd.DataFrame(get_consumption(token, start=startTime, end=endTime))
        return [dict([("ts", ts), ("val", val)]) for ts, val in zip(time, p_sol)]


class Consumption(Resource):
    def get(self):
        data = get_measured_consumption(token, start=startTime, end=endTime)
        return jsonify(data)
