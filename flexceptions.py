'''----------------------------------------------------------------------------------------------
This module contains the exceptions raised within the application
----------------------------------------------------------------------------------------------'''


class Error(Exception):
    '''Base class for exceptions in this module.'''
    pass


class FlNotFound(Error):
    '''use this when we can't find what was requested'''

    def __init__(self, m):
        self.message = 'Item NotFound: ' + m
        print self.message


class FlProviderFailure(Error):
    '''service provider unable to process'''

    def __init__(self, m):
        self.message = 'Provider failure: ' + m
        print self.message


class FlInsufficientPermission(Error):
    '''request denied due to insufficient permissions'''

    def __init__(self, m):
        self.message = 'Insufficient permission: ' + m
        print self.message
