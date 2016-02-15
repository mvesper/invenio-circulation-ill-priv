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

"""invenio-circulation-ill api utilities."""


import json
import datetime

from dateutil import relativedelta


def _get_cal_heatmap_dates(items):
    import invenio_circulation_ill.models as models

    def to_seconds(date):
        return int(date.strftime("%s"))

    def get_date_range(start_date, end_date):
        delta = (end_date - start_date).days
        res = []
        for day in range(delta+1):
            res.append(start_date + datetime.timedelta(days=day))
        return res

    res = set()
    for item in items:
        query = 'item_id:{0}'.format(item.id)
        statuses = [models.IllLoanCycle.STATUS_FINISHED,
                    models.IllLoanCycle.STATUS_CANCELED]
        clcs = models.IllLoanCycle.search(query)
        clcs = filter(lambda x: x.current_status not in statuses, clcs)
        for clc in clcs:
            date_range = get_date_range(clc.start_date, clc.end_date)
            for date in date_range:
                res.add((str(to_seconds(date)), 1))

    return dict(res)


def _get_cal_heatmap_range(items):
    import invenio_circulation_ill.models as models

    min_dates = []
    max_dates = []
    for item in items:
        query = 'item_id:{0}'.format(item.id)
        statuses = [models.IllLoanCycle.STATUS_FINISHED,
                    models.IllLoanCycle.STATUS_CANCELED]
        clcs = models.IllLoanCycle.search(query)
        clcs = filter(lambda x: x.current_status not in statuses, clcs)
        if not clcs:
            continue
        min_dates.append(min(clc.start_date for clc in clcs))
        max_dates.append(max(clc.end_date for clc in clcs))

    if not min_dates or not max_dates:
        return 0

    min_date = min(min_dates)
    max_date = max(max_dates)

    return relativedelta.relativedelta(max_date, min_date).months + 1
