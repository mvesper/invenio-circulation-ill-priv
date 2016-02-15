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

"""invenio-circulation-ill receiver to handle list signals."""


from invenio_circulation.signals import (lists_overview,
                                         lists_class)


def _lists_overview(sender, data):
    return {'name': 'ill_lists',
            'priority': 0.75,
            'result': [('Requested Inter Library Loans', 'requested_ills'),
                       ('Ordered Inter Library Loans', 'ordered_ills'),
                       ('Loaned Inter Library Loans', 'loaned_ills'),
                       ('Canceled Inter Library Loans', 'canceled_ills'),
                       ('Returned Inter Library Loans', 'returned_ills'),
                       ('Inter Library Loans Extension', 'extension_ills')]}


def _lists_class(link, data):
    from invenio_circulation_ill.lists.ills import *

    clazzes = {'requested_ills': RequestedIlls,
               'ordered_ills': OrderedIlls,
               'loaned_ills': LoanedIlls,
               'canceled_ills': CanceledIlls,
               'returned_ills': ReturnedIlls,
               'extension_ills': ExtensionIlls}

    return {'name': 'ill_lists', 'result': clazzes.get(link)}

lists_overview.connect(_lists_overview)
lists_class.connect(_lists_class)
