# -*- coding: utf-8 -*-
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
Unit tests for HistoryEntry

"""
from django.contrib.auth.models import User
from django.test import TestCase
from calorine.caro.models import HistoryEntry
from calorine.caro.models import Song
from datetime import datetime
from django.utils.timezone import utc


class HistoryEntryTests(TestCase):  # pylint: disable-msg=R0904
    """
    The profile view

    """
    def setUp(self):
        """
        Init
        """
        self.user = User.objects.create_user('admin_search',
                                             'admin_search@bar.com',
                                             'admintest')

    def test_create_historyEntry(self):
        """
        View owner historyEntrys
        """
        song = Song.objects.create(artist='Van Morrison',
                                   album='The Healing Game',
                                   title='Sometimes We Cry',
                                   genre='Blues',
                                   score=0,
                                   global_score=0)

        hist = HistoryEntry.objects.create(
            song=song,
            date_played=datetime.utcnow().replace(tzinfo=utc))

        self.assertGreater(hist.id, 0)
