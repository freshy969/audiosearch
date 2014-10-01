from __future__ import absolute_import

from django import template

from audiosearch.conf.display import ROWS_PER_TABLE as INTERVAL


register = template.Library()


@register.filter
def inspect(item):
    print '\nin filter'
    print '\t{}'.format(type(item))
    print '\t{}'.format(len(item))
    print '\t{}'.format(item)
    print 'out filter\n'
    return item












########################
########################
########################


@register.filter
def space_to_plus(url):
    # TODO use builtin iri_to_uri
    try:
        return url.replace(' ', '+')
    except AttributeError:
        return ''

