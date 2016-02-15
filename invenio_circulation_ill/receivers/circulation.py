# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""invenio-circulation-ill receiver to handle circulation signals."""


from invenio_circulation.signals import (item_returned,
                                         circulation_other_actions)


def _item_returned(sender, data):
    import invenio_circulation_ill.models as models
    import invenio_circulation_ill.api as api

    item_id = data
    res = models.IllLoanCycle.search('item_id:{0}'.format(item_id))

    if res and len(res) == 1:
        api.ill.return_ill(res[0])
        return {'name': 'ill', 'result': True}

    return {'name': 'ill', 'result': None}


def _circulation_other_actions(sender, data):
    return {'name': 'ill', 'result': [('/circulation/ill/register_ill/',
                                       'Register ILL')]}


item_returned.connect(_item_returned)
circulation_other_actions.connect(_circulation_other_actions)
