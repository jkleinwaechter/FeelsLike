from flexceptions import FlNotFound, FlProviderFailure
import pyowm
import time
import globals


################################################################################
# getWeatherString - Query the weather service and create the voice response string
#   Input:
#       location - location object (see geo.py for details)
#       metric - Use metric units if true
#       displayUnits - True if we should print out temperature units in string
#       displayLocation - True if we should print out the place name
#   Output:
#       string represnting the voice response
#   Raises:
#       FlProviderFailure - bad api call return
#       FlNotFound - bad location in request
################################################################################
def getWeatherString(location, metric, displayUnits, displayLocation):

    owm = pyowm.OWM('c1fc80b23346962803eec7881c8ab3a2')  # You MUST provide a valid API key

    try:
        start = time.time()
        observation = owm.weather_at_coords(location["lat"], location["lng"])
        globals.weatherTime = int((time.time() - start) * 1000)

    except pyowm.exceptions.not_found_error.NotFoundError:  # when an entity is not found into a collection of entities.
        raise FlNotFound("(pyowm) NotFoundError for " + str(location))
    except pyowm.exceptions.api_call_error.APICallError:  # generic failures when invoking OWM web API, in example is due to network errors.
        raise FlProviderFailure("(pywom) APICallError for " + str(location))
    except pyowm.exceptions.api_call_error.BadGatewayError:  # i.e when upstream backend cannot communicate with API gateways.
        raise FlProviderFailure("(pywom) Bad Gateway for " + str(location))
    except pyowm.exceptions.api_response_error.APIResponseError:  # HTTP error status codes in OWM web API responses.
        raise FlProviderFailure("(pyowm) APIResponseError for " + str(location))
    except pyowm.exceptions.parse_response_error.ParseResponseError:  # failures when parsing payload data in HTTP responses sent by the OWM web API.
        raise FlProviderFailure("(pyowm) ParseResponseError for " + str(location))
    except pyowm.exceptions.unauthorized_error.UnauthorizedError:  # an entity cannot be retrieved due to user subscription unsufficient capabilities.
        raise FlProviderFailure("(pyowm) Unauthorized Error")

    start = time.time()  # Keep track of time it takes for api call
    w = observation.get_weather()
    globals.weatherTime += int((time.time() - start) * 1000)  # add it to the previous invocation time - weather_at_coords

    windStruct = w.get_wind()
    humidity = w.get_humidity()
    tempStruct = w.get_temperature('fahrenheit')
    if globals.debug is True:
        print "______________WEATHER RESPONSE_______________"
        print "tempStruct:"
        print tempStruct
        print "temp = %s" % tempStruct['temp']
        print "windStruct:"
        print windStruct
        print "wind = %s" % windStruct['speed']
        print "_____________________________________________"

    temperature = tempStruct['temp']
    windSpeed = windStruct['speed']
    heatIndex = False  # default condition
    deadZone = False  # default condition

    # Make adjustment to temp
    if globals.debug is True:
        print "Temp (f): %d   Wind(mph): %d Humidity: %d" % (temperature, windSpeed, humidity)
    if temperature > 80.0:
        heatIndex = True
        if globals.debug is True:
            print "Using heat index calculations"
        feelsLike = adjustTemperature(temperature, windSpeed, humidity)
    elif temperature >= 50:  # Dead zone, do nothing
        deadZone = True
        if globals.debug is True:
            print "No adjustment needed"
        feelsLike = int(temperature)
    else:  # wind chill required
        if globals.debug is True:
            print "Wind chill calculations"
        feelsLike = adjustTemperature(temperature, windSpeed, humidity)

    '''
    The following code conditions the units for display and converts F to C if needed
        Is metric?
            Convert F->C for both original and adjusted temp
            use "Celsius" for temp
            Is wind a singular unit?
                use "kilometer per hour"
            else
                use "kilometers per hour"
        else Imperial
            use "Fahrenheit" for temp
            Is wind a singular unit?
                use "mile per hour"
            else
                use "miless per hour"
        Is temp a singular unit?
            use "degree"
        else
            use "degrees"

    '''
    tempUnits = ""  # Assume no display of temperature units. We'll correct if not
    if metric is False:
        # Handle pluralization
        if int(windSpeed) == 1 or int(windSpeed) == -1:
            windUnits = "mile"
        else:
            windUnits = "miles"  # We always display wind units
        if displayUnits is True:  # only display units for temp in certain cases as it is typically implied
            tempUnits = "Fahrenheit"
    else:  # metric
        temperature = (temperature - 32.0) * (5.0 / 9.0)  # Convert orginal temp from F to C
        feelsLike = (feelsLike - 32.0) * (5.0 / 9.0)  # Convert adjusted temp from F to C
        windSpeed = windSpeed * 1.60934  # mph -> kph
        if int(windSpeed) == 1 or int(windSpeed) == -1:  # Handle pluralization
            windUnits = "kilometer"
        else:
            windUnits = "kilometers"  # Handle pluraliation

        if globals.debug is True:
            print "Temp (c): %d   Wind (kph): %d   FeelsLike: %d" % (temperature, windSpeed, feelsLike)
        if displayUnits is True:  # only display units for temp in certain cases as it is typically implied
            tempUnits = "Celsius"

    if int(temperature) == 1 or int(temperature) == -1:  # Handle pluraliation for initial temp
        degreesOriginalPhrase = "degree"
    else:
        degreesOriginalPhrase = "degrees"

    if int(feelsLike) == 1 or int(feelsLike) == -1:  # Handle pluraliation for feels like temp
        degreesFeelsLikePhrase = "degree"
    else:
        degreesFeelsLikePhrase = "degrees"

    '''
    We need to phrase the presentation of the city dependent on what was selected
    If wihin US
        If a city
            present "City, State"
        else (could be a state, country or geogrphic entity)
            present "Geographic center of "
    else not within US
        If a city
            present "City, Country"
        else
            present "Geographic center of "
    '''
    placeString = ""  # default to no place name, unless one gets built
    if displayLocation is True:  # build the output string for this place only if needed
        if globals.debug is True:
            print "Found city"
        placeString = location["city"] + " "
        if "state" in location:
            if globals.debug is True:
                print "Found state"
            if placeString == "":  # if there is not a city, it is a larger geographic entity which may confuse the user
                if globals.debug is True:
                    print "No previous city"
                placeString = "The geographic center of "
            placeString += location["state"] + " "
        if "country" in location:
            if globals.debug is True:
                print "Found country"
            if location["country"] == "United States":
                if globals.debug is True:
                    print("and it is the US")
                if placeString == "":  # only say US if there is nothing else
                    if globals.debug is True:
                        print("and no city or state ")
                    placeString = "The geographic center of The United States"
            else:
                if globals.debug is True:
                    print "and it is foreign"
                if placeString == "":  # if there is not a city, it is a larger geographic entity which may confuse the user
                    if globals.debug is True:
                        print("and no city or state ")
                    placeString = "The geographic center of "
                placeString += location["country"]
    else:  # don't diplay the place name
        placeString = "it"  # need to bridge the empty place name to make the sentence read better

    # Build speech output
    if deadZone is True:  # 50> temp <80 is a dead zone
        speech = "The current temperature is not affected by wind or humidity. %s feels like %d %s." % (placeString, feelsLike, degreesFeelsLikePhrase)
    elif heatIndex is True:  # it's heat index
        speech = "With a %d percent humidity and a temperature of %d %s %s, %s feels like %d %s." % (humidity, temperature, degreesOriginalPhrase, tempUnits, placeString, feelsLike, degreesFeelsLikePhrase)
    else:
        speech = "With winds at %d %s per hour and a temperature of %d %s %s, %s feels like %d %s." % (windSpeed, windUnits, temperature, degreesOriginalPhrase, tempUnits, placeString, feelsLike, degreesFeelsLikePhrase)

    return speech


################################################################################
# adjustTemp - calculate windChill/heatIndex for given conditions
#   Input:
#       temp - measure temperature in degrees Fahrenheit
#       wind - wind speed in mph
#       humidity - relative humidity in percent form (e.g. 67 for 67%)
#   Output:
#       corrected temperature
################################################################################
def adjustTemperature(temp, wind, humidity):

    # We use wind chill for temps below 50, otherwise we use heat index
    if temp >= 50:  # Calculate heaat index (http://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml)
        #
        # Heat Index mode
        # This is a bit complicated in that there are special regions of exceptions.
        # Method:
        #   If heat index appears to be below 80 degress, then use the SIMPLE_EQUATION
        #   If not, use the ADVANCED_EQUATION
        #   If humidity less then 13% and temp between 80 and 87, calculate the DRY_ADJUSTMENT and subtract it from ADVANCED_EQUATION
        #   If humidity greater than 85% and temp between 80 and 120, calculate the WET_ADJUSTMENT and add it to the ADVANCED_EQUATION
        #

        #
        # SIMPLE_EQUATION
        #
        hi = 0.5 * (temp + 61 + (1.2 * (temp - 68)) + (0.094 * humidity))

        if globals.debug is True:
            print "Rough calculation: %d" % hi
        # WAverage expected heat inex with current temp to see if it looks like we may need the ADVANCED_EQUATION
        if (hi + temp) / 2 < 80:
            if globals.debug is True:
                print "Using heat index simple equation"
            return int(hi)  # simple equation sufficient

        # Need to use the more complicated formula
        if globals.debug is True:
            print "Using heat index advanced equation"
        #
        # ADVANCED_EQUATION
        #
        hi = -42.379 + (2.04901523 * temp) + (10.14333127 * humidity) - (.22475541 * temp * humidity) - (.00683783 * temp**2) \
            - (.05481717 * humidity**2) + (.00122874 * temp**2 * humidity) + (.00085282 * temp * humidity**2) - (.00000199 * temp**2 * humidity**2)

        if (80 < temp < 120) and humidity < 13:
            #
            # DRY_ADJUSTMENT
            #
            adjustment = ((13 - humidity) / 4) * ((17 - abs(temp - 95)) / 17)**.5
            if globals.debug is True:
                print "Low humidity adjustment required -%d" % adjustment
            hi -= adjustment

        if (80 < temp < 87) and humidity > 85:
            #
            # WET_ADJUSTMENT
            #
            adjustment = ((humidity - 85) / 10) * ((87 - temp) / 5)
            if globals.debug is True:
                print "High humidity adjustment required +%d" % adjustment
            hi += adjustment

        return int(hi)

    elif wind <= 3:  # wind is too small to have an effect. Return current temperature
        return int(temp)

    else:  # Calculate wind chill instead (https://en.wikipedia.org/wiki/Wind_chill)
        #
        # WIND_CHILL_EQUATION
        #
        return int(35.74 + (0.6215 * temp) - 35.75 * (wind ** 0.16) + 0.4275 * (temp * (wind**0.16)))
