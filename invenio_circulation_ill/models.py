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

"""invenio-circulation-ill database models."""


from invenio_circulation.models import ArrayType, CirculationObject
from invenio_db import db


class IllLoanCycle(CirculationObject, db.Model):
    """Data model to store inter library loan information.

    Information associated with the inter library loan cycle is stored in an
    object of this class.
    The assigned information include:
    * The corresponding user.
    * The corresponding item.
    * The desired and actual start and end date.
    """

    __tablename__ = 'ill_loan_cycle'
    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    current_status = db.Column(db.String(255))
    additional_statuses = db.Column(ArrayType(255))
    item_id = db.Column(db.BigInteger,
                        db.ForeignKey('circulation_item.id'))
    item = db.relationship('CirculationItem')
    user_id = db.Column(db.BigInteger,
                        db.ForeignKey('circulation_user.id'))
    user = db.relationship('CirculationUser')
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    desired_end_date = db.Column(db.Date)
    type = db.Column(db.String(255))
    supplier_library = db.Column(db.String(255))
    edition = db.Column(db.String(255))
    delivery = db.Column(db.String(255))
    comments = db.Column(db.String(255))
    issued_date = db.Column(db.DateTime)
    creation_date = db.Column(db.DateTime)
    modification_date = db.Column(db.DateTime)
    _data = db.Column(db.LargeBinary)

    TYPE_BOOK = 'ill_type_book'
    TYPE_ARTICLE = 'ill_type_article'

    STATUS_REQUESTED = 'requested'
    STATUS_ORDERED = 'ordered'
    STATUS_DECLINED = 'declined'
    STATUS_CANCELED = 'canceled'
    STATUS_ON_LOAN = 'on_loan'
    STATUS_EXTENSION_REQUESTED = 'extension_requested'
    STATUS_FINISHED = 'finished'
    STATUS_SEND_BACK = 'send_back'
    STATUS_MISSING = 'missing'

    STATUS_ILL_TEMPORARY = 'ill_temporary'

    EVENT_ILL_CLC_REQUEST = 'ill_clc_requested'
    EVENT_ILL_CLC_ORDERED = 'ill_clc_ordered'
    EVENT_ILL_CLC_DECLINED = 'ill_clc_declined'
    EVENT_ILL_CLC_CANCELED = 'ill_clc_canceled'
    EVENT_ILL_CLC_DELIVERED = 'ill_clc_delivered'
    EVENT_ILL_CLC_EXTENSION_REQUESTED = 'ill_clc_extension_requested'
    EVENT_ILL_CLC_FINISHED = 'ill_clc_finished'
    EVENT_ILL_CLC_SEND_BACK = 'ill_clc_send_back'
    EVENT_ILL_CLC_LOST = 'ill_clc_lost'
    EVENT_ILL_CLC_EXTENSION_CONFIRMED = 'ill_clc_extension_confirmed'
    EVENT_ILL_CLC_EXTENSION_DECLINED = 'ill_clc_extension_declined'
    EVENT_ILL_CLC_OVERDUE_LETTER_SEND = 'ill_clc_extension_declined'

    DELIVERY_DEFAULT = 'pick_up'

    _json_schema = {'type': 'object',
                    'title': 'Inter Library Loan Cycle',
                    'properties': {
                        'id': {'type': 'integer'},
                        'item_id': {'type': 'integer'},
                        'user_id': {'type': 'integer'},
                        'current_status': {'type': 'string'},
                        'supplier_library': {'type': 'string'},
                        'start_date': {'type': 'string'},
                        'end_date': {'type': 'string'},
                        'issued_date': {'type': 'string'},
                        'requested_extension_end_date': {'type': 'string'},
                        }
                    }


class IllSupplier(CirculationObject, db.Model):
    """Data model to store information regarding utilized suppliers."""

    __tablename__ = 'ill_supplier'
    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    name = db.Column(db.String(255))
    _data = db.Column(db.LargeBinary)

    _json_schema = {'type': 'object',
                    'title': 'Inter Library Loan Supplier',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        }
                    }


entities = [('Ill Loan Cycle', 'ill_loan_cycle', IllLoanCycle),
            ('Ill Supplier', 'ill_supplier', IllSupplier)]
