from __future__ import absolute_import
from itertools import chain

from audiosearch import conf

_ECHONEST_HOST = 'http://developer.echonest.com'
_ECHONEST_API = 'api'
_ECHONEST_VERSION = 'v4'
_RESPONSE_FORMAT = 'json'
_STANDARD_PARAMS = {
    'api_key': conf.ECHO_API_KEY,
    'format': _RESPONSE_FORMAT,
}

class EchoNestService(object):
    max_results = 100   # Largest size result for Echo Nest responses.


    def __init__(self, type_, method, **kwargs):
        self.dependencies = []
        self.url = '/'.join([
            _ECHONEST_HOST,
            _ECHONEST_API,
            _ECHONEST_VERSION,  
            type_,
            method])
        params = chain(_STANDARD_PARAMS.iteritems(), kwargs.iteritems())
        self.payload = dict(params)


    def __repr__(self):
        return "%s %s service" % (self._type, self._method)


