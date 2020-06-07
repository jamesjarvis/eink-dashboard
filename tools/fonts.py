import enum

class Font(enum.Enum):
  opensans = "fonts/OpenSans-SemiBold.ttf"
  robotomono = "fonts/RobotoMono-Medium.ttf"
  weather = "fonts/weatherfont.ttf"

class WeatherIcon(enum.Enum):
  """Taken straight from https://www.weatherfont.com/"""
  sunrise = '\uf051'
  sunset = '\uf052'
  celsius = '\uf03c'
  thermometer = '\uf053'
  umbrella = '\uf084'
  