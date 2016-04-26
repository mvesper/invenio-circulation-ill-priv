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

"""invenio-circulation-ill list classes."""


import invenio_circulation_ill.models as models

from flask import render_template


class BaseIlls(object):
    """invenio-circulation-ill list base class to provide the list UI."""

    positive_actions = None
    negative_actions = None

    @classmethod
    def entrance(cls):
        """List class function providing first stage user interface."""
        q = 'current_status:{0}'.format(cls.current_status)
        ill_clcs = models.IllLoanCycle.search(q)
        return render_template('lists/base_ills.html', ill_clcs=ill_clcs,
                               active_nav='lists',
                               positive_actions=cls.positive_actions,
                               negative_actions=cls.negative_actions)

    @classmethod
    def data(cls):
        """List class function providing the lists data."""
        q = 'current_status:{0}'.format(cls.current_status)
        return [{'id': x.id,
                 'item': cls._make(x),
                 'type': cls.type,
                 'positive_actions': cls.positive_actions,
                 'negative_actions': cls.negative_actions}
                for x in models.IllLoanCycle.search(q)]

    @classmethod
    def _make(cls, loan_cycle):
        item = {}
        for name, accessor in zip(cls.table_header, cls.item_accessors):
            accessors = accessor.split('.')
            tmp = loan_cycle
            try:
                for access in accessors:
                    tmp = tmp.__getattribute__(access)
            except AttributeError:
                tmp = None
            item[name] = tmp

        return item


class RequestedIlls(BaseIlls):
    """invenio-circulation-ill list to show the requested ILLs."""

    table_header = ['Borrower', 'CCID', 'Record', 'Start Date', 'End Date']
    item_accessors = ['user.name', 'user.ccid', 'item.record.title',
                      'start_date', 'end_date']
    type = 'Ill Request'
    current_status = models.IllLoanCycle.STATUS_REQUESTED
    positive_actions = [('confirm_ill_request', 'CONFIRM', 'ill_confirmation')]
    negative_actions = [('decline_ill_request', 'DECLINE')]


class OrderedIlls(BaseIlls):
    """invenio-circulation-ill list to show the ordered ILLs."""

    current_status = models.IllLoanCycle.STATUS_ORDERED
    positive_actions = [('deliver_ill', 'DELIVER', None)]
    negative_actions = [('cancel_ill_request', 'CANCEL')]


class LoanedIlls(BaseIlls):
    """invenio-circulation-ill list to show the loaned ILLs."""

    current_status = models.IllLoanCycle.STATUS_ON_LOAN
    positive_actions = [('return_ill', 'RETURN', None)]


class CanceledIlls(BaseIlls):
    """invenio-circulation-ill list to show the canceled ILLs."""

    current_status = models.IllLoanCycle.STATUS_CANCELED


class ReturnedIlls(BaseIlls):
    """invenio-circulation-ill list to show the returned ILLs."""

    current_status = models.IllLoanCycle.STATUS_FINISHED


class ExtensionIlls(object):
    """invenio-circulation-ill list showing ILLs with extension requests."""

    @classmethod
    def entrance(cls):
        """List class function providing first stage user interface.

        Showing inter library loans with requested extensions.
        """
        positive_actions = [('confirm_ill_extension', 'CONFIRM', None)]
        negative_actions = [('decline_ill_extension', 'DECLINE')]
        s = models.IllLoanCycle.STATUS_EXTENSION_REQUESTED
        q = 'additional_statuses:{0}'.format(s)
        ill_clcs = models.IllLoanCycle.search(q)
        return render_template('lists/extension_ills.html', ill_clcs=ill_clcs,
                               active_nav='lists',
                               positive_actions=positive_actions,
                               negative_actions=negative_actions)
