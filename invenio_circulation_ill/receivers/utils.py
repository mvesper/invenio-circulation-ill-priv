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

"""invenio-circulation-ill receiver to handle general signals."""


from invenio_circulation.signals import (
        circ_apis, run_action, try_action, convert_params)


def _get_action(action, try_action=False):
    import invenio_circulation_ill.api as api

    actions = {'confirm_ill_request': (api.ill, 'confirm_ill_request'),
               'decline_ill_request': (api.ill, 'decline_ill_request'),
               'deliver_ill': (api.ill, 'deliver_ill'),
               'cancel_ill_request': (api.ill, 'cancel_ill_request'),
               'confirm_ill_extension': (api.ill, 'confirm_ill_extension'),
               'decline_ill_extension': (api.ill, 'decline_ill_extension'),
               'lose_ill': (api.ill, 'lose_ill'),
               'return_ill': (api.ill, 'return_ill')}

    try_action = 'try_' if try_action else ''

    _api, func_name = actions[action]

    return getattr(_api, try_action + func_name)


def _try_action(action, data):
    from invenio_circulation.api.utils import ValidationExceptions
    from invenio_circulation.views.utils import filter_params

    try:
        filter_params(_get_action(action, True), **data)
        res = True
    except KeyError:
        res = None
    except ValidationExceptions as e:
        res = [(ex[0], str(ex[1])) for ex in e.exceptions]

    return {'name': 'ill', 'result': res}


def _run_action(action, data):
    from invenio_circulation.views.utils import filter_params

    try:
        filter_params(_get_action(action), **data)
        res = _get_message(action, data)
    except KeyError:
        res = None

    return {'name': 'ill', 'result': res}


def _get_message(action, data):
    return 'success'


def _apis(entity, data):
    import invenio_circulation_ill.api as api

    apis = {'ill_loan_cycle': api.ill}

    return {'name': 'ill', 'result': apis.get(entity)}


def _convert_params(entity, data):
    import invenio_circulation_ill.models as models

    try:
        ill_lc = models.IllLoanCycle.get(data['ill_lc_id'])
    except Exception:
        ill_lc = None

    res = {'ill_loan_cycle': ill_lc}

    return {'name': 'ill', 'result': res}


circ_apis.connect(_apis)
try_action.connect(_try_action)
run_action.connect(_run_action)
convert_params.connect(_convert_params)
