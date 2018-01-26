from random import randint
from geo import getLocationFromAlexa, getCoordinates   # Routines to pinppiont the location based on what as requested
from weather import getWeatherString  # Routines to fetch and calculate weather
import os
from flexceptions import FlProviderFailure, FlInsufficientPermission
import globals


################################################################################
# entryPoint - this is the entry point for our Feels Like lambda fucntion
#   Input:
#       event - "event" object as provided by Alexa JSON request
#       context - "context" object as provided by Alexa JSON request
#   Ouput:
#       A fully formed response card
#   Raises:
#       ValueError - not sure who is going to process this.
################################################################################
def entryPoint(event, context):

    # See if environment string has debug turned on.
    if 'debug' in os.environ:
        globals.debug = True

    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.923d8c5f-1057-45e9-8cdd-18fe3626f3b0"):
        raise ValueError("Invalid Application ID")

    #
    # New Session Request
    #
    if event["session"]["new"]:
        if globals.debug is True:
            print "New Session Request"  # Stubbed here in case we do something eventually with this
        onSessionStarted(event["request"]["requestId"], event["session"])

    #
    # Launch Request
    #
    if event["request"]["type"] == "LaunchRequest":
        if globals.debug is True:
            print "Launch Request"
        return onLaunch(event["request"], event["session"], event["context"])

    #
    # Intent Request
    #
    elif event["request"]["type"] == "IntentRequest":
        if globals.debug is True:
            print "Intent Request"
        return onIntent(event["request"], event["session"], event["context"])
    #
    # Session End Request
    #
    elif event["request"]["type"] == "SessionEndedRequest":  # stubbed here in case we do something eventually with this
        if globals.debug is True:
            print "Session End Request"
        return onSessionEnded(event["request"], event["session"])


################################################################################
# onSessionStarted - New Session Request Handler
#   Input:
#       request - "request" object as provided by Alexa JSON request
#       session - "session" object as provided by Alexa JSON request
#   Output:
#       none
################################################################################
def onSessionStarted(request, session):
    if globals.debug is True:
        print "Starting new session."


################################################################################
# onIntent - Intent Requst Handler
#   Input:
#       request - "request" object as provided by Alexa JSON request
#       session - "session" object as provided by Alexa JSON request
#       context - "context" object as probied by Alexa JSON requrst
#   Output:
#       none
#   Raises:
#       ValueError
################################################################################
def onIntent(request, session, context):
    intent = request["intent"]  # passed on to functions tht have slots
    intentName = intent["name"]
    system = context["System"]

    if intentName == "GetTemp":
        return getTemp(system)
    elif intentName == "GetTempInCity":
        return getTempInCity(system, intent)
    elif intentName == "MakingLove":
        return easterEggMakingLove()
    elif intentName == "AMAZON.HelpIntent":
        return getWelcomeResponse()
    elif intentName == "AMAZON.CancelIntent" or intentName == "AMAZON.StopIntent":
        return handleSessionEndRequest()
    else:
        if globals.debug is True:
            print "Unrecognized intent: " + str("intent")
        raise ValueError("Invalid intent")


################################################################################
# onLaunch - Launch Requst Handler
#   Input:
#       request - request object from Alexa
#       session - session object from Alexa
#       contexxt = context object from Alexa
#   Output:
#       Response card - Fully formed response card
#   Note:  the launch handler will mimic the GetTemp intent so that if someone
#       says 'ask Feels Like' they get the current temp
################################################################################
def onLaunch(request, session, context):
    return getTemp(context["System"])


################################################################################
# onSessionEnded - Session End Request Handler for nomral endings
#   Input:
#       request - "request" object as provided by Alexa JSON request
#       session - "session" object as provided by Alexa JSON request
#   Output:
#       none
################################################################################
def onSessionEnded(request, session):
    if globals.debug is True:
        print "Ending session."
    # Cleanup goes here...


################################################################################
# onSessionEnded - Process "Cancel" intent
#   Input:
#       request - "request" object as provided by Alexa JSON request
#       session - "session" object as provided by Alexa JSON request
#   Output:
#       Response card - Fully formed response card
################################################################################
def handleSessionEndRequest():
    card_title = globals.appName
    speech = "Thank you for using " + globals.appName
    shouldEndSession = True

    return buildResponse({}, buildSpeechletResponse(card_title, speech, None, shouldEndSession))


################################################################################
# GetWelcomeResponse - If allowing sessions, process a session start
#   Input:
#       request - "request" object as provided by Alexa JSON request
#       session - "session" object as provided by Alexa JSON request
#   Output:
#       Response card - Fully formed response card
################################################################################
def getWelcomeResponse():
    session_attributes = {}
    card_title = globals.appName
    speech = ("Welcome to " + globals.appName + ". What city?")
    reprompt_text = "Are you still there? "
    shouldEndSession = False

    return buildResponse(session_attributes, buildSpeechletResponse(
        card_title, speech, reprompt_text, shouldEndSession))


################################################################################
# easterEggMakingLove - easter egg response
#   Input:
#       none
#   Output:
#       Response card - Fully formed response card
################################################################################
def easterEggMakingLove():
    session_attributes = {}
    card_title = globals.appName
    phrase = ["While Roberta Flack is an amazing performer, I actually prefer the Bad Company version. ",
              "Did you know that  Roberta Flack was the first female vocalist to top the Billboard charts in three consecutive years as a result of this song?",
              "Did you know that Roberta Flack used the name Rubina Flake for her producing credit?",
              "Paul Rodgers wrote the Bad Company version of this song while staying in a commune at 19 years of age.",
              "VH1 declared this the 78th best hard rock song of all time.",
              "What in the heck was Kid Rock thinking when he tried to make a cover of this legendary Bad Company song. He's so karaoke.",
              "Who could ever forget the powerful emotion in Ned Gerblanskys voice when he sang this at Chef Aid?",
              "I'm flattered, but I am married to my job."
              ]

    speech = phrase[randint(0, len(phrase) - 1)]
    shouldEndSession = True

    return buildResponse(session_attributes, buildSpeechletResponse(
        card_title, speech, "", shouldEndSession))


################################################################################
# GetTempinCity - get the temperature from the city requested
#   Input:
#       intent - "intent" object as provided by Alexa JSON request
#   Output:
#       Response card - Fully formed response card
################################################################################
def getTempInCity(system, intent):
    deviceId = system["device"]["deviceId"]
    token = system["apiAccessToken"]
    url = system["apiEndpoint"]

    session_attributes = {}
    card_title = globals.appName
    reprompt_text = "Knock knock"
    shouldEndSession = True

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
        print "Defaulting to using Fahrenheit"
    try:   # we need to get current location to determine whether to do F/C
        origin = getLocationFromAlexa(deviceId, token, url)
        if globals.debug is True:
            print "Alexa location: " + str(origin)

    except (FlInsufficientPermission, FlProviderFailure):  # could not retrieve alexa location. Nwe'll just assume US and display units jic
        displayUnits = True
        if globals.debug is True:
            print "Displaying units because we don''t have permissions"
    else:
        displayUnits = False
        if globals.debug is True:
            print "Turning off units because we have permissions to detect the origin"
        if origin["countryCode"] != "US":
            metric = True
            if globals.debug is True:
                print "Origin is outside US - switching to celsius"

    requestedLocation = processLocationSlots(intent)
    if requestedLocation == "":  # no slots were filled respond with I don't know what to do
        speech = "I don't understand the city requested. Please try again."
    else:
        try:
            destination = getCoordinates(requestedLocation)
        except FlProviderFailure:
            speech = "I'm sorry, I appear to have had a brain fart. Please try again."
        else:
            speech = getWeatherString(destination, metric, displayUnits, True)

    print "(In City) Alexa: %d ms, Google %d ms, Weather %d ms, Location: %s" % (globals.alexaTime, globals.googleTime, globals.weatherTime, requestedLocation)
    return buildResponse(session_attributes, buildSpeechletResponse(card_title, speech, reprompt_text, shouldEndSession))


#############################################################################################
# getTemp - get the temperature from the current city designated by the device
#   Input:
#       device - device id as provided in the intent request
#       token -  token as provided in the intent request
#       baseurl - device id as provided in the intent request
#   Output:
#       fully formed respone card
#############################################################################################
def getTemp(system):
    deviceId = system["device"]["deviceId"]
    token = system["apiAccessToken"]
    url = system["apiEndpoint"]

    displayUnits = False  # never display units for home locaation
    metric = False  # default to F, unless we learn otherwise later

    session_attributes = {}
    card_title = globals.appName
    reprompt_text = "Knock knock"
    shouldEndSession = True

    # We need to get the current location (zip code). We need to make sure we have permissions
    if globals.debug is True:
        print "Device Id: %s" % (deviceId)
        print "Base URL: %s" % (url)
        print "Access token: %s" % (token)

    try:
        # First get the zip/country from Alexa, then ask Google to provide lat/lng
        r = getLocationFromAlexa(deviceId, token, url)
        locationText = r["postalCode"] + "," + r["countryCode"]
        location = getCoordinates(locationText)
        if globals.debug is True:
            print "Alexa permissions granted"

    except FlProviderFailure:
        speech = "I'm sorry, I appear to have had a brain fart. Please try again."
    except FlInsufficientPermission:
        speech = ('<speak>I need to have permission to use your zip code to report the temperature at your location. '
                  'You can do this by selecting <s> <emphasis level="moderate">Your Skills</emphasis></s> from the Alexa app, choosing, '
                  '<s><emphasis level="moderate">' + globals.appName + '</emphasis></s>, and then select <s><emphasis level="moderate">Settings.</emphasis> </s>'
                  '<p>If you do not want to enable this permission, I can still report on select cities. '
                  'Just say <s> <prosody rate="120%">Alexa, ask ' + globals.appName + ' in Cumming Georgia.</prosody></s></p></speak>')
        if globals.debug is True:
            print "No Alexa permission, but required. Informing user"
        return buildResponse(session_attributes, buildPermsNeededResponse(speech))
    else:
        if location["country"] != "United States":
            metric = True
            if globals.debug is True:
                print "Going to celsius because we are not in the United States"

        speech = getWeatherString(location, metric, displayUnits, False)

    print "(Local) Alexa: %d ms, Google %d ms, Weather %d ms  Location: %s" % (globals.alexaTime, globals.googleTime, globals.weatherTime, locationText)
    return buildResponse(session_attributes, buildSpeechletResponse(card_title, speech, reprompt_text, shouldEndSession))


################################################################################
# ProcessLocationSlots - Decode the various combinations of locations
#   Input:
#       intent - "intent" object as provided by Alexa JSON request
#   Output:
#       A string suitable for passing to the geo locator system
#################################################################################
def processLocationSlots(intent):
    result = ""

    if "CITY" in intent["slots"]:
        slot = intent["slots"]["CITY"]
        if "value" in slot:
            city = slot["value"].lower()
            result = city

    if "STATE" in intent["slots"]:
        slot = intent["slots"]["STATE"]
        if "value" in slot:
            state = slot["value"].lower()
            if result == "":
                result = state
            else:
                result += "," + state

    if "COUNTRY" in intent["slots"]:
        slot = intent["slots"]["COUNTRY"]
        if "value" in slot:
            country = slot["value"].lower()
            if result == "":
                result = country
            else:
                result += "," + country

    return result


################################################################################
# buildResponse - create fully formed response card
#   Input:
#       session_attributes - The session_attributes of the
#           fully formed response card
#       speechlet_response - the voice portion of the
#           fully formed response card
#   Output:
#       Fully formed response card. This can be sent back to Alexa
################################################################################
def buildResponse(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }


################################################################################
# buildSpeechletResponse - build the response part of the response caard
#   Input:
#       title - text placed on title of card
#       output - the voice response that will also be used in the card body
#       reprompt - text to use for open session that are not completed
#       shouldEndSession - Boolean indicating wheter to close session or not
#   Output:
#       Fully formed "response" portion of a card.  Note this is not the full card
################################################################################
def buildSpeechletResponse(title, output, reprompt, shouldEndSession):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt
            }
        },
        "shouldEndSession": shouldEndSession
    }


################################################################################
# buildPermsNeededResponse - Handle getting permissions from user
#   Input:
#       output - the string you would like read to the user in SSML.
#   Output:
#       Fully formed "response" portion of card. Note this is not the full card
################################################################################
def buildPermsNeededResponse(output):

    return {
        "outputSpeech": {
            "type": "SSML",
            "ssml": output
        },
        "card": {
            "type": "AskForPermissionsConsent",
            "title": "Permission Request",
            "permissions": ["read::alexa:device:all:address"],
            "content": output
        },
        "shouldEndSession": True
    }
