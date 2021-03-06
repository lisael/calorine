# -*- coding: utf-8 -*-  pylint: disable-msg=R0801
#
# Copyright (c) 2012 Rodolphe Quiédeville <rodolphe@quiedeville.org>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
The django views
"""
import json
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render
from calorine.caro.models import Song
from calorine.caro.models import Logs
from calorine.caro.models import PlaylistEntry
from calorine.caro.models import HistoryEntry
from calorine.caro.models import Vote
from calorine.caro.models import Stream
from datetime import datetime
from django.views.generic import ListView
from django.core.cache import cache
from haystack.query import SearchQuerySet


class SongList(ListView):
    paginate_by = 17
    template_name = "songs.html"
    context_object_name = "songs"

    def get_queryset(self):
        try:
            qry_str = self.request.GET.get('q')
        except NameError:
            qry_str = None

        if qry_str is not None:
            srchqry = SearchQuerySet().filter(
                content__contains=qry_str).models(Song)
            results = [r.pk for r in srchqry]
            queryset = Song.objects.filter(pk__in=results)
        else:
            queryset = Song.objects.filter(score__gte=0, family=0)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SongList, self).get_context_data(**kwargs)
        for song in context['songs']:
            if cache.get('song_{}'.format(song.pk)):
                song.vote = True
        return context


class HistoryList(ListView):
    queryset = HistoryEntry.objects.all().order_by("-date_played")
    paginate_by = 17
    template_name = 'history.html'
    context_object_name = "songs"


class PlayList(ListView):
    queryset = PlaylistEntry.objects.all().order_by('-score', 'date_add')
    paginate_by = 17
    template_name = 'playlist.html'
    context_object_name = "songs"

    def get_context_data(self, **kwargs):
        context = super(PlayList, self).get_context_data(**kwargs)
        for ple in context['songs']:
            if cache.get('ple_{}_{}'.format(self.request.user.id,
                                            ple.song.pk,
                                            ple.pk)):
                ple.vote = True
        return context


class LogList(ListView):
    queryset = Logs.objects.all().order_by('-date_import')
    template_name = 'errors.html'
    context_object_name = 'errors'
    paginate_by = 17


def profile(request):
    """The profile wiew
    """
    ples = PlaylistEntry.objects.all().order_by('-pk', 'date_add')[:4]
    songs = Song.objects.all().order_by('-pk')[:4]
    streams = Stream.objects.all()
    template_name = 'profile.html'

    return render(request,
                  template_name,
                  {'songs': songs,
                   'ples': ples,
                   'streams': streams
                   })

def onair(request):
    """The onair
    """
    try:
        artist = cache.get('onair_artist')
    except:
        artist = ''

    try:
        title = cache.get('onair_title')
    except:
        title = ''

    try:
        album = cache.get('onair_album')
    except:
        album = ''


    datas = {'artist': artist,
             'title': title,
             'album': album}

    response = HttpResponse(mimetype='application/json; charset=utf-8')

    from json import dumps
    response.write(json.dumps(datas))

    return response



def pladd(request, song_id):
    """
    The songs in databases
    """
    song = get_object_or_404(Song, pk=song_id)

    ple = PlaylistEntry(song=song,
                        score=1,
                        date_add=datetime.today())
    ple.save()
    pllike(request, ple.pk)
    return render(request, 'playlist_add.html')


def pldislike(request, pk):
    """
    dislike a song in Playlist
    """
    return inc_desc("less", request, pk)


def pllike(request, pk):
    """
    Like a song
    """
    return inc_desc("plus", request, pk)


def inc_desc(sign, request, pk):
    """
    Need doc
    """
    ple = get_object_or_404(PlaylistEntry, pk=pk)
    key = 'ple_{}_{}'.format(request.user.id, ple.song.pk, ple.pk)
    song_key = 'song_{}'.format(ple.song.pk)
    song = get_object_or_404(Song, pk=ple.song.id)

    vote = Vote(song=song, user=request.user)
    vote.save()

    if cache.get(key):
        return HttpResponse(
            json.dumps({'message': 'Do not try this with me'}),
            mimetype="application/json")
    else:
        cache.set(key, True)
        cache.set(song_key, True)

    if sign == "plus":
        ple.score += 1
    else:
        ple.score -= 1
    ple.save()
    resp = {'score': ple.score, 'id': ple.pk}
    return HttpResponse(
        json.dumps({'entry': resp}),
        mimetype="application/json")
