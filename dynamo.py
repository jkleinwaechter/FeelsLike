'''----------------------------------------------------------------------------------------------
This contains the methods to manage any Dynamo database operations
----------------------------------------------------------------------------------------------'''
import boto3
import globals
from json import dumps
import datetime
# from flexceptions import FlNotFound, FlProviderFailure


class Record(object):
    '''----------------------------------------------------------------------------------------------
    Class used to encapsualte the dynamo db record. This is used to get a history of how people are
    using this skill.

    Methods
    -------
        write()
            Commit current record to db.

    Setters
    -------
        cid(cc)
            c : string
                The customer id as provided in the 'userId' section of the JSON Request object
        source(s)
            s : string
                The location of the Alexa device
        destination(d)
            d: string
                The location requested
        intent(i)
            i : string
                Name of the intent that was invoked

    Getters
    -------
        cid()
        spreadsheetId()

    ----------------------------------------------------------------------------------------------'''

    def __init__(self, cid='n/a', intent='n/a'):
        self._cid = cid
        self._intent = intent
        self._source = 'n/a'
        self._destination = 'n/a'
        # initialize database access
        self._ddb = boto3.resource('dynamodb', region_name='us-east-1')
        self._table = self._ddb.Table('feelslike')

    def write(self):
        count = 1

        # If record already exists, just incrment count and update time
        response = self._table.get_item(Key={'cid': self.cid, 'destination': self._destination})
        if 'Item' in response:
            if 'count' in response['Item']:
                count = response['Item']['count'] + 1

        time = datetime.datetime.now().strftime('%a %d-%b-%y %I:%M%p')

        self._record = {'cid': self._cid, 'source': self._source, 'destination': self._destination, 'intent': self._intent, 'count': count, 'time': time}
        if globals.debug:
            print self._record

        if globals.debug:
            print response
        response = self._table.put_item(Item=self._record)
        if globals.debug:
            print '--------------------------DYNAMO-------------------------'
            print response
            print dumps(response, indent=4)
            print '---------------------------------------------------------'

        return response

    @property
    def cid(self):
        return self._cid

    @cid.setter
    def cid(self, c):
        self._cid = c

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, s):
        self._source = s

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, d):
        self._destination = d

    @property
    def intent(self):
        return self._intent

    @intent.setter
    def intent(self, i):
        self._intent = i
