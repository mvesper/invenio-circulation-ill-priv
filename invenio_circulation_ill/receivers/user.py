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

"""invenio-circulation-ill receiver to handle user signals."""


from invenio_circulation.signals import user_current_holds


def _user_current_holds(sender, data):
    import json
    import invenio_circulation_ill.models as models

    from flask import render_template
    from invenio_circulation_ill.api.utils import (
            _get_cal_heatmap_dates, _get_cal_heatmap_range)

    def make_dict(clc):
        return {'clc': clc,
                'cal_data': json.dumps(_get_cal_heatmap_dates([clc.item])),
                'cal_range': _get_cal_heatmap_range([clc.item])}

    user_id = data
    SL = models.IllLoanCycle.STATUS_ON_LOAN
    SR = models.IllLoanCycle.STATUS_REQUESTED
    SO = models.IllLoanCycle.STATUS_ORDERED

    query = 'user_id:{0} current_status:{1}'.format(user_id, SL)
    current_holds = [make_dict(clc) for clc
                     in models.IllLoanCycle.search(query)]

    query = 'user_id:{0} current_status:{1}'.format(user_id, SR)
    requested_holds = [make_dict(clc) for clc
                       in models.IllLoanCycle.search(query)]

    query = 'user_id:{0} current_status:{1}'.format(user_id, SO)
    ordered_holds = [make_dict(clc) for clc
                     in models.IllLoanCycle.search(query)]

    return {'name': 'ill', 'priority': 0.7,
            'result': [render_template('user/ill_current_holds.html',
                                       holds=current_holds),
                       render_template('user/ill_requested_holds.html',
                                       holds=requested_holds),
                       render_template('user/ill_ordered_holds.html',
                                       holds=ordered_holds)]}

user_current_holds.connect(_user_current_holds)
