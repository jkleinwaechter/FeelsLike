'''----------------------------------------------------------------------------------------------
This module handles the division of labor for each of the intents. For this skill, most of the
business logic is contained in this module
----------------------------------------------------------------------------------------------'''
import globals
from random import randint
from geo import getLocationFromAlexa, getCoordinates   # Routines to pinppiont the location based on what as requested
from weather import getWeatherString  # Routines to fetch and calculate weather
from cards import buildResponse, buildSpeechletResponse, buildPermsNeededResponse
from flexceptions import FlProviderFailure, FlInsufficientPermission
from dynamo import Record


def intentWelcome(cid):
    '''----------------------------------------------------------------------------------------------
    If allowing sessions, process a session start

    Parameters
    ----------
        cid : string
            The customer id as provided in the 'userId' section of the JSON Request object

    Returns
    -------
        dictionary
            The Alexa JSON Response object
    ----------------------------------------------------------------------------------------------'''
    session_attributes = {}
    card_title = globals.appName
    speech = ('Welcome to ' + globals.appName + '. What city?')
    reprompt_text = 'Are you still there? '
    shouldEndSession = False

    return buildResponse(session_attributes,
                         buildSpeechletResponse(title=card_title, output=speech, prompt=reprompt_text,
                                                largeImage='', smallImage='', shouldEndSession=shouldEndSession))


def intentMakingLove(cid):
    '''----------------------------------------------------------------------------------------------
    Process the easter egg response

    Parameters
    ----------
        cid : string
            The customer id as provided in the 'userId' section of the JSON Request object

    Returns
    -------
        dictionary
            The Alexa JSON Response object
    ----------------------------------------------------------------------------------------------'''
    session_attributes = {}
    card_title = globals.appName
    phrase = ['While Roberta Flack is an amazing performer, I actually prefer the Bad Company version. ',
              'Did you know that  Roberta Flack was the first female vocalist to top the Billboard charts in three consecutive years as a result of this song?',
              'Did you know that Roberta Flack used the name Rubina Flake for her producing credit?',
              'Paul Rodgers wrote the Bad Company version of this song while staying in a commune at 19 years of age.',
              'VH1 declared this the 78th best hard rock song of all time.',
              'What in the heck was Kid Rock thinking when he tried to make a cover of this legendary Bad Company song. He\'s so karaoke.',
              'Who could ever forget the powerful emotion in Ned Gerblanskys voice when he sang this at Chef Aid?',
              'I\'m flattered, but I am married to my job.'
              ]

    speech = phrase[randint(0, len(phrase) - 1)]
    shouldEndSession = True

    # commit to database
    # record the userdId for potential database write
    db = Record(cid, 'Making Love')
    db.write()

    return buildResponse(session_attributes,
                         buildSpeechletResponse(title=card_title, output=speech, reprompt='',
                                                largeImage='', smallImage='', shouldEndSession=shouldEndSession))


def intentUnique(place, cid):
    '''----------------------------------------------------------------------------------------------
    Process requests for otherworldly place like Heavern, Hell, Sun, and Moon

    Parameters
    ----------
        place : string
            One of the special locations
        cid : string
            The customer id as provided in the 'userId' section of the JSON Request object

    Returns
    -------
        dictionary
            The Alexa JSON Response object
    ----------------------------------------------------------------------------------------------'''
    session_attributes = {}
    card_title = globals.appName
    smallImage = ''
    largeImage = ''

    # record the userdId for potential database write
    db = Record(cid, 'Unique Location')

    if place == 'GetTempInHeaven':  # source:  http://w.astro.berkeley.edu/~gmarcy/thermal/tpteacher/jokes/heaven.html
        # Fill in data for eventual database write
        db.destination = 'Heaven'
        speech = ('The temperature of Heaven can be rather accurately computed from available data. Our authority is the Bible: Isiah 30:26 reads, '
                  '"Moreover the light of the moon shall be as the light of the sun and the light of the sin shall be sevenfold, as the light of seven days." '
                  'Thus Heaven receives from the moon as much radiation as we do from the sun and in addition seven times seven or 49 times as much as the earth does '
                  'from the sun, or fifty times in all. The light we receive from the moon is a ten-thousandth of the light we receive from the sun, so we can ignore that. '
                  'With this data we can compute the temperature of Heaven. The radiation falling on heaven will heat it to the point lost by radiation is just equal '
                  'to the heat received by radiation. In other words, Heaven loses fifty times as much heat as the earth by radiation. Using the Stefan-Boltzmann '
                  'fourth-power law for radiation ( H <sub alias="divided by">/</sub> E ) <sub alias="to the fourth power">^4</sub> = 50, where E is the absolute temperature'
                  'of the earth - 300K. This gives H as 798 Kelvin or 525 degrees Celsius.')
        largeImage = globals.pixUrl + 'heavenlarge.jpg'
        smallImage = globals.pixUrl + 'heavensmall.jpg'

    elif place == 'GetTempInHell':
        # Fill in data for eventual database write
        db.destination = 'Hell'
        speech = ('It depends on which level of hell you mean. Most of it feels like a fiery lake of burning sulfur. However, in the Cocytus, a place far removed from all '
                  'light and warmth, it is a place so cold that only those in Dickinson North Dakota could comprehend.')
        largeImage = globals.pixUrl + 'helllarge.jpg'
        smallImage = globals.pixUrl + 'hellsmall.jpg'

    elif place == 'GetTempOnSun':
        # Fill in data for eventual database write
        db.destination = 'Sun'
        speech = ('It is currently 27 million degrees Fahrenheit. However, if you are planning to visit, I recommend staying out in the convective zone where it '
                  'is only 3 million degrees.')
        largeImage = globals.pixUrl + 'sunlarge.jpg'
        smallImage = globals.pixUrl + 'sunsmall.jpg'

    elif place == 'GetTempOnMoon':
        # Fill in data for eventual database write
        db.destination = 'Moon'
        speech = ('On the dark side it is currently -298 degrees Fahrenheit. This doesn\'t Speak to Me, especially if I try to Breathe In the Air. At this temperature '
                  'I\'d have to be constantly On the Run hoping I didn\'t run out of long underwear before I got to see the big Eclipse. You\'d have to have a lot of Time, '
                  'Money, and Brain Damage to stay here. But hey, between Us and Them, Any Colour You Like is ok with me. We all have our adventures before that '
                  'Great Gig in the Sky.')
        largeImage = globals.pixUrl + 'moonlarge.jpg'
        smallImage = globals.pixUrl + 'moonsmall.jpg'
    else:
        if globals.debug:
            print 'Could not find intent: ' + place
        speech = 'Are you sure that place even has weather?'

    shouldEndSession = True

    # commit to database
    db.write()

    return buildResponse(session_attributes,
                         buildSpeechletResponse(title=card_title, output=speech, reprompt='',
                                                largeImage=largeImage, smallImage=smallImage, shouldEndSession=shouldEndSession))


################################################################################
# intentTempInCity - get the temperature from the city requested
#   Input:
#       intent - 'intent' object as provided by Alexa JSON request
#   Output:
#       Response card - Fully formed response card
################################################################################
def intentTempInCity(system, intent, cid):
    '''----------------------------------------------------------------------------------------------
    Get the feels like temperature for a specified city

    Parameters
    ----------
        system : dictionary
            The 'system' section of the Alexa JSON Request object
        intent : dictionary
            The 'intent' section of the Alexa JSON Request object
        cid : string
            The customer id as provided in the 'userId' section of the JSON Request object

    Returns
    -------
        dictionary
            The Alexa JSON Response object
    ----------------------------------------------------------------------------------------------'''
    largeImage = ''
    smallImage = ''

    deviceId = system['device']['deviceId']
    token = system['apiAccessToken']
    url = system['apiEndpoint']

    session_attributes = {}
    card_title = globals.appName
    reprompt_text = 'Knock knock'
    shouldEndSession = True

    # Fill in data for eventual database write
    db = Record(cid, 'City Specified')

    if globals.debug:
        print 'intentTempInCity'

    ''' Here's the logic for determining metric or imperial units and whether to display units
            If Alexa gives device location
                Don't display units
                Within the US?
                    use imperial
                Else
                    use metric
            If Alexa does not give device location
                Display units
                Use imperial
    '''
    metric = False  # Assume Imperial units to start with. Overide if not true
    if globals.debug is True:
        print 'Defaulting to using Fahrenheit'
    try:   # we need to get current location to determine whether to do F/C
        pc, cc = getLocationFromAlexa(deviceId, token, url)
        loc = pc + ',' + cc
        # add source for eventual db write
        db.source = str(loc)

        if globals.debug is True:
            print 'Alexa location: ' + loc

    except (FlInsufficientPermission, FlProviderFailure):  # could not retrieve alexa location. Nwe'll just assume US and display units jic
        displayUnits = True
        if globals.debug is True:
            print 'Displaying units because we don''t have permissions'
    else:
        displayUnits = False
        if globals.debug is True:
            print 'Turning off units because we have permissions to detect the origin'
        if cc != 'US':
            metric = True
            if globals.debug is True:
                print 'Origin is outside US - switching to celsius'

    requestedLocation = processLocationSlots(intent)
    if requestedLocation == '':  # no slots were filled respond with I don't know what to do
        speech = 'I don\'t understand the city requested. Please try again.'
    else:
        try:
            destination = getCoordinates(requestedLocation)
        except FlProviderFailure:
            speech = 'I\'m sorry, I appear to have had a brain fart. Please try again.'
        else:
            # add destination for eventual db write
            db.destination = ''
            if 'city' in destination:
                db.destination += destination['city']
            if 'state' in destination:
                if db.destination != '':
                    db.destination += ','
                db.destination += destination['state']
            if 'country' in destination:
                if db.destination != '':
                    db.destination += ','
                db.destination += destination['country']

            speech, largeImage, smallImage = getWeatherString(destination, metric, displayUnits, True)
            db.write()  # commit to database

    print '(In City) Alexa: %d ms, Google %d ms, Weather %d ms, Location: %s' % (globals.alexaTime, globals.googleTime, globals.weatherTime, requestedLocation)

    return buildResponse(session_attributes,
                         buildSpeechletResponse(title=card_title, output=speech, reprompt=reprompt_text,
                                                largeImage=largeImage, smallImage=smallImage, shouldEndSession=shouldEndSession))


def intentTemp(system, cid):
    '''----------------------------------------------------------------------------------------------
    Report the temperature for the place where the alexa device has recorded as home

    Parameters
    ----------
        system : dictionary
            The 'system' section of the Alexa JSON Request object
        cid : string
            The customer id as provided in the 'userId' section of the JSON Request object

    Returns
    -------
        dictionary
            The Alexa JSON Response object
    ----------------------------------------------------------------------------------------------'''
    largeImage = ''
    smallImage = ''
    deviceId = system['device']['deviceId']
    token = system['apiAccessToken']
    url = system['apiEndpoint']

    displayUnits = False  # never display units for home locaation
    metric = False  # default to F, unless we learn otherwise later

    session_attributes = {}
    card_title = globals.appName
    reprompt_text = 'Knock knock'
    shouldEndSession = True

    # Fill in data for eventual database write
    db = Record(cid, 'No City')

    if globals.debug:
        print 'intentTemp'

    # We need to get the current location (zip code). We need to make sure we have permissions
    if globals.debug is True:
        print 'Device Id: %s' % (deviceId)
        print 'Base URL: %s' % (url)
        print 'Access token: %s' % (token)

    try:
        # First get the zip/country from Alexa, then ask Google to provide lat/lng
        pc, cc = getLocationFromAlexa(deviceId, token, url)
        locationText = pc + ',' + cc
        db.source = locationText
        location = getCoordinates(locationText)
        if globals.debug is True:
            print 'Alexa permissions granted'

    except FlProviderFailure:
        speech = 'I\'m sorry, I appear to have had a brain fart. Please try again.'
    except FlInsufficientPermission:
        speech = ('<speak>I need to have permission to use your zip code to report the temperature at your location. '
                  'You can do this by selecting <s> <emphasis level="moderate">Your Skills</emphasis></s> from the Alexa app, choosing, '
                  '<s><emphasis level="moderate">' + globals.appName + '</emphasis></s>, and then select <s><emphasis level="moderate">Settings.</emphasis> </s>'
                  '<p>If you do not want to enable this permission, I can still report on select cities. '
                  'Just say <s> <prosody rate="120%">Alexa, ask ' + globals.appName + ' in Cumming Georgia.</prosody></s></p></speak>')
        if globals.debug is True:
            print 'No Alexa permission, but required. Informing user'
        return buildResponse(session_attributes, buildPermsNeededResponse(speech))
    else:
        if location['country'] != 'United States':
            metric = True
            if globals.debug is True:
                print 'Going to celsius because we are not in the United States'

        speech, largeImage, smallImage = getWeatherString(location, metric, displayUnits, False)

    # add destination for eventual db write
    db.destination = ''
    if 'city' in location:
        db.destination += location['city']
    if 'state' in location:
        if db.destination != '':
            db.destination += ','
        db.destination += location['state']
    if 'country' in location:
        if db.destination != '':
            db.destination += ','
        db.destination += location['country']
    db.write()  # commit to database

    print '(Local) Alexa: %d ms, Google %d ms, Weather %d ms  Location: %s' % (globals.alexaTime, globals.googleTime, globals.weatherTime, locationText)
    return buildResponse(session_attributes,
                         buildSpeechletResponse(title=card_title, output=speech, reprompt=reprompt_text,
                                                largeImage=largeImage, smallImage=smallImage, shouldEndSession=shouldEndSession))


def intentEndSession(cid):
    '''----------------------------------------------------------------------------------------------
    Process 'Cancel' intent

    Parameters
    ----------
        cid : string
            The customer id as provided in the 'userId' section of the JSON Request object

    Returns
    -------
        dictionary
            The Alexa JSON Response object
    ----------------------------------------------------------------------------------------------'''
    card_title = globals.appName
    speech = 'Thank you for using ' + globals.appName
    shouldEndSession = True

    return buildResponse({}, buildSpeechletResponse(title=card_title, output=speech, reprompt='',
                                                    largeImage='', smallImage='', shouldEndSession=shouldEndSession))


def processLocationSlots(intent):
    '''----------------------------------------------------------------------------------------------
    Decode the various combinations in the city clot

    Parameters
    ----------
        intent : dictionary
            The 'intent' section of the Alexa JSON Request object

    Returns
    -------
        string
            A location suitable for passing to the geo location functions (e.g. City, State, Country)
    ----------------------------------------------------------------------------------------------'''
    result = ''

    if 'CITY' in intent['slots']:
        slot = intent['slots']['CITY']
        if 'value' in slot:
            city = slot['value'].lower()
            result = city

    if 'STATE' in intent['slots']:
        slot = intent['slots']['STATE']
        if 'value' in slot:
            state = slot['value'].lower()
            if result == '':
                result = state
            else:
                result += ',' + state

    if 'COUNTRY' in intent['slots']:
        slot = intent['slots']['COUNTRY']
        if 'value' in slot:
            country = slot['value'].lower()
            if result == '':
                result = country
            else:
                result += ',' + country

    return result
