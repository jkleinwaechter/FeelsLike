from flexceptions import FlProviderFailure, FlInsufficientPermission
from json import loads
import requests
import time
import globals


################################################################################
# These functions determine the latitude and longitude for the
# location the user requested, or defaulted to for his device
# The returning location structure looks as follows:
# {
#    "lat":"",
#    "lng":"",
#    "country":"",
#    "state":"",
#    "city":""
# }
# Note that all fields will be filled in regarldess of the minimal
# information provided. If you simply provide a zip code, for example,
# these functions will extrapolate the other fields. If the request
# is for a plcae outside the US, 'state' is not provided
################################################################################


################################################################################
# getLocationFromAlexa - query Alexa for location in lat/lng
#   Input:
#       deviceId - the deiceId sent in the intent JSON
#       token -  the token sent in the intent JSON
#       baseUrl -the url  sent in the intent JSON
#   Output:
#       dict - {"countryCode" : "US", "postalCode" : "30024"}
#   Raises:
#       FlProviderFailure - something went wrong in the communication
#       FlInsufficientPermission - skill does not have necessary permission to read location
################################################################################
def getLocationFromAlexa(deviceId, token, baseUrl):

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

    return response


################################################################################
# getCoordinatess - get the lat/lng of the city specified
#   Input:
#       site - string containing the location. Preferred format
#           is prints to append entities by a comma, but not required.
#           This is typically city/state, city/country, or zip
#   Output:
#       location - a location object as described at the top
#           note that the lat/lng pair returned defaults to the
#           geographic center of the location as determined by
#           Google.
#
#   Examples:
#       getCorrdiantes("Rome") (ambiguous, but still works)
#       getCorrdiantes("Rome, USA") (better, but still amiguous)
#       getCorrdiantes("Rome, Georgia") (perfect)
#       getCorrdiantes("30363") (valid, but slightly ambiguous)
#       getCorrdiantes("30363, USA") (perfect)
#       getCorrdiantes("France") (valid, but is it meaningful?)
#   Raises:
#       FlProviderFailure - something went wrong in the communication
################################################################################
def getCoordinates(site):
    gkey = "Insert your google api geocode key here"
    location = {}

    # https://maps.googleapis.com/maps/api/geocode/json?address=Suwanee&key=AIzaSyBvzejn3gPuixmWEYCqCY3TonLspA1tP7o

    # transactionJSON = dumps(payload)  # Convert payload dictionary to JSON
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + site + "&key=" + gkey

    httpHeader = {'Accept': 'application/json'}

    if globals.debug is True:
        print "Requesting location for %s" % site

    # Make the Google geocode call
    try:
        start = time.time()  # We record in the log all api call lengths
        jsonResponse = requests.get(url, headers=httpHeader)
        globals.googleTime = int((time.time() - start) * 1000)

    except requests.exceptions.TooManyRedirects:
        raise FlProviderFailure("(Google) Too many redirects")
    except requests.exceptions.Timeout:
        raise FlProviderFailure("(Google) Timeout")
    except requests.exceptions.ConnectionError:
        raise FlProviderFailure("(Google) Could not connect")
    except requests.exceptions.RetryError:
        raise FlProviderFailure("(Google) Retry failure")
    else:
        if jsonResponse.ok is True:  # If result is good, convert to Dict and return
            isContinent = False
            response = loads(jsonResponse.text)
            if globals.debug is True:
                print "______________GOOGLE RESPONSE________________"
                print jsonResponse.text
                print "_____________________________________________"
            base = response["results"][0]
            location["lat"] = base["geometry"]["location"]["lat"]
            location["lng"] = base["geometry"]["location"]["lng"]

            # Parse the various ways Google could describe an entity
            for address in base["address_components"]:
                long_name = address["long_name"]
                for kind in address["types"]:
                    if kind == "country":
                        location["country"] = long_name
                    elif kind == "administrative_area_level_1":  # we are only interested in this if this is US, as this will be the state
                        location["state"] = long_name
                    elif kind == "locality":  # this is the city if one was specified. This will be non-existant if only a country was given
                        location["city"] = long_name
                    elif kind == "postal_town":  # This is how some europeancities get registered
                        location["city"] = long_name
                    elif kind == "establishment":  # this is a place name rather than a specific city (e.g. Mt Washington)
                        location["city"] = long_name
                    elif kind == "continent":  # Why would someone ask, who knows, but lets track it anyway
                        location["country"] = long_name
                        isContinent = True

            if location["country"] != "United States":  # we aren't supporting mid level govenrment entities outside the US.
                if "state" in location:
                    del location["state"]

            if isContinent:  # since this is a continent, we need to remove the fact that it is also a natural feature so we dont duplicate place name
                if "city" in location:
                    del location["city"]

        else:
            raise FlProviderFailure("(Google) Could not process request: " + str(jsonResponse.status_code) + " : " + jsonResponse.text)

        if globals.debug is True:
            print "GeoCode location: " + str(location)

    return location
