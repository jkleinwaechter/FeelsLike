'''----------------------------------------------------------------------------------------------
This module handles the geolocation aspects of the skill
----------------------------------------------------------------------------------------------'''
from flexceptions import FlProviderFailure, FlInsufficientPermission
from json import loads
import requests
import time
import globals


def getLocationFromAlexa(deviceId, token, baseUrl):
    '''----------------------------------------------------------------------------------------------
    Quesry Alexa for location

    Parameters
    ----------
        deviceId - string
            The deiceId sent in the intent JSON
        token : string
            The token sent in the intent JSON
        baseUrl : string
            The url  sent in the intent JSON

    Returns
    -------
        string
            Postal code
        string
            Country Code

    Raises
    ------
        FlProviderFailure - something went wrong in the communication
        FlInsufficientPermission - skill does not have necessary permission to read location

    ----------------------------------------------------------------------------------------------'''
    # transactionJSON = dumps(payload)  # Convert payload dictionary to JSON

    auth = "Bearer " + token
    url = baseUrl + "/v1/devices/" + deviceId + "/settings/address"
    httpHeader = {'Authorization': auth, 'Accept': 'application/json'}

    if globals.debug is True:
        print "Http header: %s" % httpHeader
        print "Url: %s" % url

    # Make the Alexa API call
    try:
        start = time.time()  # we report time in the logs for each api call
        jsonResponse = requests.get(url, headers=httpHeader)
        globals.alexaTime = int((time.time() - start) * 1000)

    except requests.exceptions.TooManyRedirects:
        raise FlProviderFailure("(Alexa) Too many redirects.")
    except requests.exceptions.ConnectionError:
        raise FlProviderFailure("(Alexa) Connection Error")
    except requests.exceptions.Timeout:
        raise FlProviderFailure("(Alexa) Timeout")
    except requests.exceptions.ConnectionError:
        raise FlProviderFailure("(Alexa) Could not connect.")
    except requests.exceptions.RetryError:
        raise FlProviderFailure("(Alexa) Retry failure")
    else:
        if jsonResponse.ok is True:
            response = loads(jsonResponse.text)
            if globals.debug is True:
                print "______________ALEXA RESPONSE_________________"
                print response
                print "_____________________________________________"
        elif jsonResponse.status_code == 403:  # Forbidden (403) - indicates that the user has nt enabled permissions. We need to take action to allow them to do so, or at least give them a message.
            raise FlInsufficientPermission("(Alexa) Zip code access")  # See https://developer.amazon.com/docs/custom-skills/device-address-api.html for how-to information
        else:  # likely bad j
            raise FlProviderFailure("(Alexa) Could not process request: " + str(jsonResponse.status_code) + " : " + jsonResponse.text)
    cc = response["countryCode"]
    if cc == "US":  # due to change in google api, we will need to shorten US zip codes to 5 digits
        pc = response["postalCode"][:5]
    else:
        pc = response["postalCode"]

    return pc, cc


def getCoordinates(site):
    '''----------------------------------------------------------------------------------------------
    Get the Lat/Lng of the location specified

    Parameters
    ----------
        site : string
            Location to process. Preferred format is prints to append entities by a comma,
            but not required. This is typically city/state, city/country, or zip

    Returns
    -------
        dictionary
            A location object that is centered geogrphacially to the region specified

    Raises
    ------
        FlProviderFailure - something went wrong in the communication

    Examples
    --------
        getCorrdiantes("Rome") (ambiguous, but still works)
        getCorrdiantes("Rome, USA") (better, but still amiguous)
        getCorrdiantes("Rome, Georgia") (perfect)
        getCorrdiantes("30363") (valid, but slightly ambiguous)
        getCorrdiantes("30363, USA") (perfect)
        getCorrdiantes("France") (valid, but is it meaningful?)
    Note
    ----
        All fields will be filled in regarldess of the minimal information provided. If you simply
        provide a zip code, for example, these functions will extrapolate the other fields. If the
        request is for a place outside the US, 'state' is not provided

    ----------------------------------------------------------------------------------------------'''

    location = {}

    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + site + '&key=' + globals.gkey

    httpHeader = {'Accept': 'application/json'}

    if globals.debug is True:
        print 'Requesting location for %s' % site
        print url

    # Make the Google geocode call
    try:
        start = time.time()  # We record in the log all api call lengths
        jsonResponse = requests.get(url, headers=httpHeader)
        globals.googleTime = int((time.time() - start) * 1000)

    except requests.exceptions.TooManyRedirects:
        raise FlProviderFailure('(Google) Too many redirects')
    except requests.exceptions.Timeout:
        raise FlProviderFailure('(Google) Timeout')
    except requests.exceptions.ConnectionError:
        raise FlProviderFailure('(Google) Could not connect')
    except requests.exceptions.RetryError:
        raise FlProviderFailure('(Google) Retry failure')
    else:
        if jsonResponse.ok is True:  # If result is good, convert to Dict and return
            isContinent = False
            response = loads(jsonResponse.text)
            if globals.debug is True:
                print '______________GOOGLE RESPONSE________________'
                print jsonResponse.text
                print '_____________________________________________'
            if response['status'] == 'ZERO_RESULTS':  # Google responding, but not with any coordinate data.
                raise FlProviderFailure('(Google) Could not process request: ' + str(jsonResponse.status_code) + ' : ' + jsonResponse.text)

            base = response['results'][0]
            location['lat'] = base['geometry']['location']['lat']
            location['lng'] = base['geometry']['location']['lng']

            # Parse the various ways Google could describe an entity
            for address in base['address_components']:
                long_name = address['long_name']
                for kind in address['types']:
                    if kind == 'country':
                        location['country'] = long_name
                    elif kind == 'administrative_area_level_1':  # we are only interested in this if this is US, as this will be the state
                        location['state'] = long_name
                    elif kind == 'locality':  # this is the city if one was specified. This will be non-existant if only a country was given
                        location['city'] = long_name
                    elif kind == 'postal_town':  # This is how some europeancities get registered
                        location['city'] = long_name
                    elif kind == 'establishment':  # this is a place name rather than a specific city (e.g. Mt Washington)
                        location['city'] = long_name
                    elif kind == 'continent':  # Why would someone ask, who knows, but lets track it anyway
                        location['country'] = long_name
                        isContinent = True

            if location['country'] != 'United States':  # we aren't supporting mid level govenrment entities outside the US.
                if 'state' in location:
                    del location['state']

            if isContinent:  # since this is a continent, we need to remove the fact that it is also a natural feature so we dont duplicate place name
                if 'city' in location:
                    del location['city']

        else:
            raise FlProviderFailure('(Google) Could not process request: ' + str(jsonResponse.status_code) + ' : ' + jsonResponse.text)

        if globals.debug is True:
            print 'GeoCode location: ' + str(location)

    return location
