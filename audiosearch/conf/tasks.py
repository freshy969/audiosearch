"""Abstract task class definitions"""

from __future__ import absolute_import
import os

from audiosearch.cache.redis import RedisCache
from audiosearch.conf import settings


class SharedConnectionMixin(object):
    """Enforce all tasks executed in a worker's subprocess to use the same
    audiosearch cache client.
    """

    _cache = None


    @property
    def Cache(self):
        if self._cache is None:
            pid = os.getpid()
            worker_subprocess = 'worker @ {}'.format(pid)
            self._cache = RedisCache(worker_subprocess, settings.CACHE_CONFIG)
        return self._cache


