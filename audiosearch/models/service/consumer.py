from __future__ import absolute_import
import logging
from time import sleep

from requests import get, RequestException

from audiosearch import messages
from audiosearch.services.base import EmptyResponseError, ServiceError


logger = logging.getLogger("general_logger")

_ATTEMPT_LIMIT = 15
_CALL_SNOOZE = 2    # In seconds.

# EchoNest response codes.
_SUCCESS = 0
_LIMIT_EXCEEDED = 3
_MISSING_PARAM = 4
_INVALID_PARAM = 5

class EchoCodeError(Exception):
    pass

class NoDataError(Exception):
    pass

class TimeoutError(Exception):
    pass




def consume(package):
    attempt = 0
    print package.url

    while True:
        try:
            if attempt > _ATTEMPT_LIMIT: raise TimeoutError()

            response = get(package.url, params=package.payload)
            json_response = response.json()

            status_code = json_response['response']['status']['code']
            status_message = json_response['response']['status']['message']

            # Response is valid, branch on echo nest code.
            if status_code == _SUCCESS:
                data = json_response['response'][package.ECHO_NEST_KEY]
                break

            # Exceeded API access limit.  Snooze then retry.
            elif status_code == _LIMIT_EXCEEDED:
                attempt += 1
                sleep(_CALL_SNOOZE)

            # TODO: make this less fragile.  Check echo nest docs.
            elif "does not exist" in status_message:
                raise EchoCodeError(status_message)

            # Received error code in response.
            else:
                raise EchoCodeError(status_code)

        # Invalid request or unable to parse json response.
        except (EchoCodeError, KeyError, RequestException, ValueError) as e:
            logger.exception(e)
            raise NoDataError()
            break

        except TimeoutError:
            logger.exception(response)
            raise NoDataError()
            break

    return data

    