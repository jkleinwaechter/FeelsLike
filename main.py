'''----------------------------------------------------------------------------------------------
This is the main entry function and distributor for all Alexa invocations
----------------------------------------------------------------------------------------------'''
import os
import globals
from intents import intentWelcome, intentMakingLove, intentUnique, intentTemp, intentTempInCity, intentEndSession


def entryPoint(event, context):
    '''----------------------------------------------------------------------------------------------
    The main entry point for an AWS Lambda function.

    Parameters
    ----------
        event : dict
            AWS event data. The dictionary representation of the Alexa JSON Request object
        context : dict
            AWS Lambda context object (unused)

    Returns
    -------
        dictionary
            The Alexa JSON Response object

    Notes
    -----
        https://docs.aws.amazon.com/lambda/latest/dg/python-programming-model-handler-types.html
        https://developer.amazon.com/docs/custom-skills/request-and-response-json-reference.html

    ----------------------------------------------------------------------------------------------'''

    # See if environment string has debug turned on.
    if 'debug' in os.environ:
        globals.debug = True

    if (event['session']['application']['applicationId'] != globals.skillId):
        raise ValueError('Invalid Application ID')

    #
    # New Session Request
    #
    if event['session']['new']:
        if globals.debug is True:
            print 'New Session Request'  # Stubbed here in case we do something eventually with this
        onSessionStarted(event['request']['requestId'], event['session'])

    #
    # Launch Request
    #
    if event['request']['type'] == 'LaunchRequest':
        if globals.debug is True:
            print 'Launch Request'
        return onLaunch(event['request'], event['session'], event['context'])

    #
    # Intent Request
    #
    elif event['request']['type'] == 'IntentRequest':
        if globals.debug is True:
            print 'Intent Request'
        return onIntent(event['request'], event['session'], event['context'])
    #
    # Session End Request
    #
    elif event['request']['type'] == 'SessionEndedRequest':  # stubbed here in case we do something eventually with this
        if globals.debug is True:
            print 'Session End Request'
        return onSessionEnded(event['request'], event['session'])


def onSessionStarted(request, session):
    '''----------------------------------------------------------------------------------------------
    Process an Alexa New Session Request

    Parameters
    ----------
        request : dictionary
            The 'request' section of the Alexa JSON Request object
        session : dictionary
            The 'session' section of the Alexa JSON Request object

    Returns
    -------
        none

    ----------------------------------------------------------------------------------------------'''

    if globals.debug is True:
        print 'Starting new session.'


def onIntent(request, session, context):
    '''----------------------------------------------------------------------------------------------
    Process an Alexa Intent Request

    Parameters
    ----------
        request : dictionary
            The 'request' section of the Alexa JSON Request object
        session : dictionary
            The 'session' section of the Alexa JSON Request object
        context : dictionary
            The 'context' section of the Alexa JSON Request object

    Returns
    -------
        dictionary
            The Alexa JSON Response object

    Raises
    ------
        ValueError
            Invalid intent
    ----------------------------------------------------------------------------------------------'''

    intent = request['intent']  # passed on to functions tht have slots
    intentName = intent['name']
    system = context['System']
    cid = session['user']['userId']

    if globals.debug:
        print 'Intent: ' + intentName

    if intentName == 'GetTemp':
        return intentTemp(system, cid)
    elif intentName == 'GetTempInCity':
        return intentTempInCity(system, intent, cid)
    elif intentName == 'MakingLove':
        return intentMakingLove(cid)
    elif intentName in {'GetTempInHeaven', 'GetTempinHell', 'GetTempOnSun', 'GetTempOnMoon'}:
        return intentUnique(intentName, cid)
    elif intentName == 'AMAZON.HelpIntent':
        return intentWelcome(cid)
    elif intentName == 'AMAZON.CancelIntent' or intentName == 'AMAZON.StopIntent':
        return intentEndSession(cid)
    else:
        if globals.debug is True:
            print 'Unrecognized intent: ' + str(intentName)
        return intentUnique(intentName, cid)  # Let's pass it as an easter egg attemnpt


def onLaunch(request, session, context):
    '''----------------------------------------------------------------------------------------------
    Process an Alexa Launch Request. This is used when an Alexa skill is invoked with no parameters

    Parameters
    ----------
        request : dictionary
            The 'request' section of the Alexa JSON Request object
        session : dictionary
            The 'session' section of the Alexa JSON Request object
        context : dictionary
            The 'context' section of the Alexa JSON Request object

    Returns
    -------
        dictionary
            The Alexa JSON Response object

    Note
    ----
        The launch handler will mimic the intentTemp intent so that if someone says 'ask Feels Like',
        they get the current temp.
    ----------------------------------------------------------------------------------------------'''

    if globals.debug:
        print 'OnLaunch'
    return intentTemp(context['System'], session['user']['userId'])


def onSessionEnded(request, session):
    '''----------------------------------------------------------------------------------------------
    Process an Alexa Session End Request. Not to be confused with a Stop or Cancel event.

    Parameters
    ----------
        request : dictionary
            The 'request' section of the Alexa JSON Request object
        session : dictionary
            The 'session' section of the Alexa JSON Request object

    Returns
    -------
        dictionary
            The Alexa JSON Response object
    ----------------------------------------------------------------------------------------------'''

    if globals.debug is True:
        print 'onSessionEnd'
    # Cleanup goes here...
