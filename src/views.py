import ast
import json
import urllib

from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context

from src import services, utils, tasks
from audiosearch.redis import client as cache
from audiosearch.config import DEBUG_TOOLBAR


def index(request, **kwargs):
    context = Context({})

    return render(request, 'index.html', context)


def search(request, **kwargs):
    prefix = "search:"
    resource_id = urllib.unquote_plus(request.GET.get('q'))
    resource = prefix + resource_id
    page = request.GET.get('page')
    page_type = request.GET.get('type')

    context = Context({
        'resource': resource,
        'resource_id': resource_id,
        'type': page_type,
        'page': page,
        'debug': kwargs.get('debug'),
    })

    service_map = {
        'search_artists': services.SearchArtists(resource_id),
        'search_songs': services.SearchSongs(None, resource_id),
    }

    content = utils.generate_content(resource, service_map, page=page)
    context.update(content)

    try:
        print
        # print type(content['similar_songs']['data'])
        print "search_artists: %s" % content['search_artists']['data'][0].keys()
        print "search_songs: %s" % content['search_songs']['data'][0].keys()
        print
    except KeyError:
        pass

    return render(request, "search.html", context)


def artist(request, **kwargs):
    prefix = "artist:"
    resource_id = urllib.unquote_plus(kwargs['artist'])
    resource = prefix + resource_id

    context = Context({
        'resource': resource,
        'resource_id': resource_id,
        'debug': kwargs.get('debug'),
    })

    service_map = {
        'profile': services.ArtistProfile(resource_id),
        'songs': services.ArtistSongs(resource_id),
        'similar_artists': services.SimilarArtists(resource_id),
        'similar_songs': services.SimilarSongs(resource_id, "artist"),
    }

    content = utils.generate_content(resource, service_map)
    context.update(content)

    try:
        print
        # print type(content['similar_songs']['data'])
        print "songs: %s" % content['songs']['data'][0].keys()
        print "similar_artists: %s" % content['similar_artists']['data'][0].keys()
        print "similar_songs: %s" % content['similar_songs']['data'][0].keys()
        print
    except KeyError:
        pass

    return render(request, "artist.html", context)


def artist_songs(request, **kwargs):
    artist = kwargs['artist']
    page = request.GET.get('page')
    context = Context({
        'dir_name': urllib.unquote_plus(artist),
        'page': page,
        'debug': kwargs.get('debug'),
    })

    service_map = {
        'profile': services.ArtistProfile(artist),
        'songs': services.ArtistSongs(artist),
    }

    content = utils.generate_content(artist, service_map, page=page)
    context.update(content)

    return render(request, "artist-songs.html", context)


def song(request, **kwargs):
    prefix = "song:"
    artist_id = urllib.unquote_plus(kwargs['artist'])
    resource_id = urllib.unquote_plus(kwargs['song'])
    resource = prefix + artist_id + ":" + resource_id

    context = Context({
        'dir_artist': artist_id,
        'dir_song': resource_id,
        'debug': kwargs.get('debug'),
    })

    service_map = {
        'profile': services.SongProfile(artist_id, resource_id),
        'similar_artists': services.SimilarArtists(artist),
        'similar_songs': services.SimilarSongs(resource_id, "song", artist_id, song_id=resource_id),
    }

    content = utils.generate_content(resource, service_map)
    context.update(content)

    return render(request, "song.html", context)


def similar(request, **kwargs):
    artist = urllib.unquote_plus(kwargs['artist'])
    song = kwargs.get('song')
    page = request.GET.get('page')
    display_type = request.GET.get('type')
    resource_type = "song" if song else "artist"

    if song:
        song = urllib.unquote_plus(song)
        prefix = "song:"
        resource_id = song
        resource = prefix + artist + ":" + song
        service_map = {
            'profile': services.SongProfile(artist, resource_id),
        }

    else:
        prefix = "artist:"
        resource_id = artist
        resource = prefix + resource_id
        service_map = {
            'profile': services.ArtistProfile(resource_id),
        }

    if not display_type or display_type == "songs":
        service_map['similar_songs'] = services.SimilarSongs(resource_id, resource_type, artist_id=artist, song_id=song)
    
    if not display_type or display_type == "artists":
        service_map['similar_artists'] = services.SimilarArtists(artist)

    context = Context({
        'dir_artist': artist,
        'dir_song': song,
        'resource': resource,
        'resource_id': resource_id,
        'resource_type': resource_type,
        'page': page,
        'debug': kwargs.get('debug'),
    })

    content = utils.generate_content(resource, service_map, page=page)
    context.update(content)

    print
    print type(content['similar_songs']['data'])
    print content['similar_songs']['data'][0]
    print

    return render(request, "similar.html", context)


# HTTP 500
def server_error(request):
    response = render(request, "500.html")
    response.status_code = 500
    return response


"""
-------------------------------------
Functions for handling ASYNC requests
-------------------------------------
"""

def retrieve_content(request, **kwargs):
    resource = utils.unescape_html(request.GET.get('resource'))
    content_key = request.GET.get('content_key')
    page = request.GET.get('page')
    context = {}

    content_string = cache.hget(resource, content_key)

    if not content_string: 
        context['status'] = 'pending'

        return HttpResponse(json.dumps(context), content_type="application/json")

    content = ast.literal_eval(content_string)
    context['status'] = 'success'

    try:
        context[content_key] = utils.page_resource(page, content)
    except TypeError:
        context[content_key] = content

    return HttpResponse(json.dumps(context), content_type="application/json")








def retrieve_resource(request):
    id_ = request.GET.get('q')
    rtype = request.GET.get('rtype')
    page = request.GET.get('page')

    if cfg.REDIS_DEBUG:
        cache.delete(id_)

    context = {}
    resource_string = cache.hget(id_, rtype)

    if resource_string:
        resource = ast.literal_eval(resource_string)

        if rtype == "profile":
            context[rtype] = resource
        else:
            context = util.page_resource_async(page, resource, rtype)

        context['q'] = id_
        context['status'] = "ready"

    else:
        context['status'] = "pending"

    if cfg.VIEW_DEBUG and context['status'] == "ready":
        util.inspect_context(context)

    return HttpResponse(json.dumps(context), content_type="application/json")


def clear_resource(request):
    resource = utils.unescape_html(request.GET.get('resource'))
    hit = cache.delete(resource)

    pre = "REMOVED," if hit else "NOT FOUND,"
    banner = '\'' * len(pre)

    print
    print banner
    print "%s %s" %(pre, resource)
    print banner
    print

    return HttpResponse(json.dumps({}), content_type="application/json")


def debug_template(request):
    # utils.print_cache(utils.local_cache)

    return HttpResponse(json.dumps({}), content_type="application/json")
