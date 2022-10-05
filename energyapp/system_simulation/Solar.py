import pvlib
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

P_RADIATION = 1000  # W/m2


class Solar:

    def __init__(self, roof_area, surface_tilt, surface_azimuth, module):

        self.latitude = None
        self.longitude = None
        self.tz = 'CET'
        self.surface_tilt = surface_tilt
        self.surface_azimuth = surface_azimuth
        self.sun_zen = 0
        self.air_mass = 0
        self.roof_area = roof_area
        self.efficiency = None
        self.module = module

    def get_coordinates(self, city):
        try:
            geolocator = Nominatim(user_agent="Enefso")
            location = geolocator.geocode(city)
            self.longitude = location.longitude
            self.latitude = location.latitude
        except GeocoderTimedOut or GeocoderUnavailable:
            self.longitude = 2.3514992
            self.latitude = 48.8566101
            print("Can't connect to geolocator")

    def calc_irrad(self, times):
        altitude = 20
        weather = pvlib.iotools.get_pvgis_tmy(self.latitude, self.longitude, map_variables=True)[0]
        weather.index.name = "time"
        # Change the year of TMY to match the year defined by the user
        weather.reset_index(inplace=True)
        weather["time"] = weather["time"].apply(lambda x: x.replace(year=times.year[0]))
        weather.set_index("time", inplace=True)
        solpos = pvlib.solarposition.get_solarposition(
            time=weather.index,
            latitude=self.latitude,
            longitude=self.longitude,
            altitude=altitude,
            temperature=weather["temp_air"],
            pressure=pvlib.atmosphere.alt2pres(altitude),
        )
        dni_extra = pvlib.irradiance.get_extra_radiation(weather.index)
        self.air_mass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
        pressure = pvlib.atmosphere.alt2pres(altitude)
        am_abs = pvlib.atmosphere.get_absolute_airmass(self.air_mass, pressure)
        aoi = pvlib.irradiance.aoi(
            self.surface_tilt,
            self.surface_azimuth,
            solpos["apparent_zenith"],
            solpos["azimuth"],
        )
        total_irradiance = pvlib.irradiance.get_total_irradiance(
            self.surface_tilt,
            self.surface_azimuth,
            solpos['apparent_zenith'],
            solpos['azimuth'],
            weather['dni'],
            weather['ghi'],
            weather['dhi'],
            dni_extra=dni_extra,
            model='isotropic',
            surface_type='urban'
        )

        return total_irradiance, weather, am_abs, aoi

    def pv_system(self, irradiation, weather, am_abs, aoi):

        sandia_modules = pvlib.pvsystem.retrieve_sam(name='SandiaMod')
        sandia_module = sandia_modules[self.module]
        temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
        cell_temperature = pvlib.temperature.sapm_cell(
            irradiation['poa_global'],
            weather["temp_air"],
            weather["wind_speed"],
            **temperature_model_parameters,
        )
        effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(
            irradiation['poa_direct'],
            irradiation['poa_diffuse'],
            am_abs,
            aoi,
            sandia_module,
        )

        dc = pvlib.pvsystem.sapm(effective_irradiance, cell_temperature, sandia_module)

        module_area = sandia_module.loc['Area']
        I_mp = sandia_module.loc['Impo']
        V_mp = sandia_module.loc['Vmpo']
        self.efficiency = (I_mp * V_mp) / (module_area * P_RADIATION)

        total_power = dc['p_mp'] / module_area * self.roof_area

        return total_power

    def get_resampled_irradiation(self, irradiation, time_range, freq):
        if "min" in freq:
            # if freq is in minutes then upsample and use linear interpolation. Else sum the values for downsampling
            irradiation_resampled = irradiation.resample(freq).interpolate(method='linear')
        else:
            irradiation_resampled = irradiation.resample(freq).mean()
        irradiation_resampled = irradiation_resampled[time_range[0]:time_range[-1]]
        return irradiation_resampled.values

    def get_resampled_solar_power(self, P_solar, time_range, freq):
        if "min" in freq:
            # if freq is in minutes then upsample and use linear interpolation. Else sum the values for downsampling
            P_solar_resampled = P_solar.resample(freq).interpolate(method='linear')
        else:
            P_solar_resampled = P_solar.resample(freq).mean()
        P_solar_resampled = P_solar_resampled[time_range[0]:time_range[-1]]
        return P_solar_resampled.values
