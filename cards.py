'''----------------------------------------------------------------------------------------------
This module is responsible for building the components of the Alexa JSON Repsonse objects
----------------------------------------------------------------------------------------------'''
import globals
import re


def buildResponse(session_attributes, speechlet_response):
    '''----------------------------------------------------------------------------------------------
    Create a fully formed Alexa JSON Response object

    Parameters
    ----------
        sessionAttributes : dictionary
            State variables that will be returned to us while in the same session
        speechletResponse : dictionary
            The 'response' section of the Alexa JSON Response object

    Returns
    -------
    dictionary
        The Alexa JSON Response object
    ----------------------------------------------------------------------------------------------'''
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def buildSpeechletResponse(title, output, reprompt, largeImage, smallImage, shouldEndSession):
    '''----------------------------------------------------------------------------------------------
    Build the 'response' section of the Alexa JSON Response object

    Parameters
    ----------
        title : string
            Text placed on title of card
        output : string
            SSML voice response, excluding the <speak> tags
        reprompt : string
            Voice response if user does not respond in time
        shouldEndSession - boolean
            Request that this be the end of the session

    Returns
    -------
        'Response' section of the Alexa JSON Response object

    ----------------------------------------------------------------------------------------------'''
    if smallImage == '':
        smallImage = globals.pixUrl + 'flDefaultSmallImage.jpg'
    if largeImage == '':
        largeImage = globals.pixUrl + 'flDefaultLargeImage.jpg'

    # add the speak tag around the object so that the incoming text can be pure text or ssmal.
    voice = '<speak>' + output + '</speak>'  # Using SSML, but we will take care of enclosing the string in a speak tag

    # Strip out ssml so we can print to the card
    cleanr = re.compile('<.*?>')
    cleanOutput = re.sub(cleanr, '', output)
    if globals.debug:
        print 'CleanOutput: ' + cleanOutput

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': voice
        },
        'card': {
            'type': 'Standard',
            'title': title,
            'text': cleanOutput,
            'image': {
                'smallImageUrl': smallImage,
                'largeImageUrl': largeImage
            },
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt
            }
        },
        'shouldEndSession': shouldEndSession
    }


def buildPermsNeededResponse(output):
    '''----------------------------------------------------------------------------------------------
    Handle invalid permissions for app

    Parameters
    ----------
        output : string
            Speech given to user

    Returns
    -------
        'Response' section of the Alexa JSON Response object

    ----------------------------------------------------------------------------------------------'''

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'AskForPermissionsConsent',
            'title': 'Permission Request',
            'permissions': ['read::alexa:device:all:address'],
            'content': output
        },
        'shouldEndSession': True
    }
