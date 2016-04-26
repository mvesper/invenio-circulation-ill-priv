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

"""invenio-circulation-ill api responsible for IllLoanCycle handling."""


from invenio_circulation.api.item import create as create_item
from invenio_circulation.api.item import lose_items
from invenio_circulation.api.event import create as create_event
from invenio_circulation.api.utils import email_notification
from invenio_circulation.api.utils import ValidationExceptions

from invenio_circulation.models import (CirculationItem,
                                        CirculationLoanCycle)
from invenio_circulation_ill.models import IllLoanCycle


def _create_ill_temporary_item(record):
    ill_tmp = 'ill_temporary_no_value'
    status = CirculationItem.STATUS_ON_SHELF
    group = CirculationItem.GROUP_BOOK
    item = create_item(record.id, 1, ill_tmp, ill_tmp, ill_tmp, ill_tmp,
                       ill_tmp, ill_tmp, status, group)
    item.additional_statuses = [IllLoanCycle.STATUS_ILL_TEMPORARY]
    item.save()

    return item


def request_ill(user, record, start_date, end_date,
                delivery=None, comments='', type=None):
    """Request inter library loan for the given record to the given user.

    :param record: Invenio Record.
    :param user: CirculationUser.
    :param start_date: Start date of the loan (without time).
    :param end_date: End date of the loan (without time).
    :param delivery: 'pick_up' or 'internal_mail'
    :param comments: Comments regarding the inter library loan.

    :return: Created IllLoanCycle
    """
    delivery = IllLoanCycle.DELIVERY_DEFAULT if delivery is None else delivery
    type = IllLoanCycle.TYPE_BOOK if type is None else type

    item = _create_ill_temporary_item(record)

    ill_clc = IllLoanCycle.new(current_status=IllLoanCycle.STATUS_REQUESTED,
                               item=item, user=user,
                               start_date=start_date, end_date=end_date,
                               delivery=delivery, comments=comments,
                               type=type)

    create_event(user_id=user.id, item_id=item.id,
                 ill_loan_cycle_id=ill_clc.id,
                 event=IllLoanCycle.EVENT_ILL_CLC_REQUEST)

    email_notification('ill_request', 'john.doe@cern.ch', user.email,
                       name=user.name, action='requested', items=item)

    return ill_clc


def try_confirm_ill_request(ill_loan_cycle):
    """Check the conditions to confirm a given requested inter library loan.

    Checked conditions:
    * The current_status must be 'requested'.

    :param ill_loan_cycle: Requested inter library loan.
    """
    exceptions = []
    try:
        assert ill_loan_cycle.current_status == IllLoanCycle.STATUS_REQUESTED,\
                'The ill loan cycle is in the wrong state'
    except AssertionError as e:
        exceptions.append(('ill', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def confirm_ill_request(ill_loan_cycle, supplier_id, comments=''):
    """Confirm the given inter library loan request.

    The ill_loan_cycles current_status will be set to 'ordered'.

    :param supplier_id: Id of the chosen IllSupplier.

    :raise: ValidationExceptions
    """
    try:
        try_confirm_ill_request(ill_loan_cycle)
    except ValidationExceptions as e:
        raise e

    ill_loan_cycle.current_status = IllLoanCycle.STATUS_ORDERED
    ill_loan_cycle.supplier_id = supplier_id
    ill_loan_cycle.comments = comments
    ill_loan_cycle.save()

    create_event(ill_loan_cycle_id=ill_loan_cycle.id,
                 event=IllLoanCycle.EVENT_ILL_CLC_ORDERED)

    email_notification('ill_ordered', 'john.doe@cern.ch',
                       ill_loan_cycle.user.email,
                       ill_loan_cycle=ill_loan_cycle)


def try_cancel_ill_request(ill_loan_cycle):
    """Check the conditions to cancel the inter library loan.

    Checked conditions:
    * The current_status must be 'requested' or 'ordered'.

    :raise: ValidationExceptions
    """
    exceptions = []
    try:
        sr = IllLoanCycle.STATUS_REQUESTED
        so = IllLoanCycle.STATUS_ORDERED
        msg = 'The ill loan cycle is in the wrong state'
        assert (ill_loan_cycle.current_status == sr or
                ill_loan_cycle.current_status == so), msg
    except AssertionError as e:
        exceptions.append(('ill', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def cancel_ill_request(ill_loan_cycle, reason=''):
    """Cancel the given inter library loan.

    The ill_loan_cycles current_status will be set to 'canceled'.
    :raise: ValidationExceptions
    """
    try:
        try_cancel_ill_request(ill_loan_cycle)
    except ValidationExceptions as e:
        raise e

    ill_loan_cycle.current_status = IllLoanCycle.STATUS_CANCELED
    ill_loan_cycle.save()

    create_event(ill_loan_cycle_id=ill_loan_cycle.id,
                 event=IllLoanCycle.EVENT_ILL_CLC_CANCELED,
                 description=reason)


def try_decline_ill_request(ill_loan_cycle):
    """Check the conditions to decline the inter library loan request.

    Checked conditions:
    * The current_status must be 'requested'.

    :raise: ValidationExceptions
    """
    exceptions = []
    try:
        sr = IllLoanCycle.STATUS_REQUESTED
        msg = 'The ill loan cycle is in the wrong state'
        assert ill_loan_cycle.current_status == sr, msg
    except AssertionError as e:
        exceptions.append(('ill', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def decline_ill_request(ill_loan_cycle, reason=''):
    """Decline the given inter library loan request.

    The ill_loan_cycles current_status will be set to 'declined'.
    :raise: ValidationExceptions
    """
    try:
        try_decline_ill_request(ill_loan_cycle)
    except ValidationExceptions as e:
        raise e

    ill_loan_cycle.current_status = IllLoanCycle.STATUS_DECLINED
    ill_loan_cycle.save()

    create_event(ill_loan_cycle_id=ill_loan_cycle.id,
                 event=IllLoanCycle.EVENT_ILL_CLC_DECLINED,
                 description=reason)

    email_notification('ill_declined', 'john.doe@cern.ch',
                       ill_loan_cycle.user.email,
                       ill_loan_cycle=ill_loan_cycle)


def try_deliver_ill(ill_loan_cycle):
    """Check the conditions to deliver the inter library loan.

    Checked conditions:
    * The current_status must be 'ordered'.

    :raise: ValidationExceptions
    """
    exceptions = []
    try:
        assert ill_loan_cycle.current_status == IllLoanCycle.STATUS_ORDERED, \
                'The ill loan cycle is in the wrong state'
    except AssertionError as e:
        exceptions.append(('ill', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def deliver_ill(ill_loan_cycle):
    """Deliver the given inter library loan.

    The items current_status will be set to 'on_loan'.
    The ill_loan_cycles current_status will be set to 'on_loan'.
    :raise: ValidationExceptions
    """
    try:
        try_deliver_ill(ill_loan_cycle)
    except ValidationExceptions as e:
        raise e

    import invenio_circulation.models as models

    ill_loan_cycle.current_status = IllLoanCycle.STATUS_ON_LOAN
    ill_loan_cycle.save()

    ill_loan_cycle.item.current_status = models.CirculationItem.STATUS_ON_LOAN
    ill_loan_cycle.item.save()

    create_event(ill_loan_cycle_id=ill_loan_cycle.id,
                 event=IllLoanCycle.EVENT_ILL_CLC_DELIVERED)

    email_notification('ill_delivery', 'john.doe@cern.ch',
                       ill_loan_cycle.user.email,
                       ill_loan_cycle=ill_loan_cycle)


def try_request_ill_extension(ill_loan_cycle):
    """Check the conditions to request an inter library loan extension.

    Checked conditions:
    * The current_status must be 'on_loan'.

    :raise: ValidationExceptions
    """
    exceptions = []
    try:
        sol = CirculationLoanCycle.STATUS_ON_LOAN
        msg = 'The ill loan cycle is in the wrong state'
        assert ill_loan_cycle.current_status == sol, msg
    except AssertionError as e:
        exceptions.append(('ill', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def request_ill_extension(ill_loan_cycle, requested_end_date):
    """Request an extension for the given inter library loan.

    'extension_requested' will be added to the attribute additional_statuses.
    The desired_end_date will be set to requested_end_date.
    :raise: ValidationExceptions
    """
    try:
        try_request_ill_extension(ill_loan_cycle)
    except ValidationExceptions as e:
        raise e

    ser = IllLoanCycle.STATUS_EXTENSION_REQUESTED
    ill_loan_cycle.desired_end_date = requested_end_date
    ill_loan_cycle.additional_statuses.append(ser)
    ill_loan_cycle.save()

    create_event(ill_loan_cycle_id=ill_loan_cycle.id,
                 event=IllLoanCycle.EVENT_ILL_CLC_EXTENSION_REQUESTED)

    email_notification('ill_extension_request', 'john.doe@cern.ch',
                       ill_loan_cycle.user.email,
                       loan_cycle=ill_loan_cycle)


def try_confirm_ill_extension(ill_loan_cycle):
    """Check the conditions to confirm the inter library loan extension.

    Checked conditions:
    * The current_status must be 'on_loan'.
    * The additional_statuses must contain 'extension_requested'.

    :raise: ValidationExceptions
    """
    exceptions = []
    try:
        assert ill_loan_cycle.current_status == IllLoanCycle.STATUS_ON_LOAN, \
               'The ill loan cycle is in the wrong state'
    except AssertionError as e:
        exceptions.append(('ill', e))

    try:
        s = IllLoanCycle.STATUS_EXTENSION_REQUESTED
        msg = 'The ill loan cycle is in the wrong state'
        assert s in ill_loan_cycle.additional_statuses, msg
    except AssertionError as e:
        exceptions.append(('ill', e))

    try:
        assert ill_loan_cycle.desired_end_date is not None, \
                'A desired end date is necessary.'
    except AssertionError as e:
        exceptions.append(('ill', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def confirm_ill_extension(ill_loan_cycle):
    """Confirm the requested extension for the given inter library loan.

    The end_date and desired_end_date attributes will be adjusted.
    'extension_requested' will be removed from additional_statuses.
    :raise: ValidationExceptions
    """
    try:
        try_confirm_ill_extension(ill_loan_cycle)
    except ValidationExceptions as e:
        raise e

    ser = IllLoanCycle.STATUS_EXTENSION_REQUESTED
    ill_loan_cycle.end_date = ill_loan_cycle.desired_end_date
    ill_loan_cycle.desired_end_date = None
    ill_loan_cycle.additional_statuses.remove(ser)
    ill_loan_cycle.save()

    create_event(ill_loan_cycle_id=ill_loan_cycle.id,
                 event=IllLoanCycle.EVENT_ILL_CLC_EXTENSION_CONFIRMED)

    email_notification('ill_extension_request_confirmed', 'john.doe@cern.ch',
                       ill_loan_cycle.user.email,
                       loan_cycle=ill_loan_cycle)


def try_decline_ill_extension(ill_loan_cycle):
    """Check the conditions to decline the inter library loan extension.

    Checked conditions:
    * The current_status must be 'on_loan'.
    * The additional_statuses must contain 'extension_requested'.

    :raise: ValidationExceptions
    """
    exceptions = []
    try:
        assert ill_loan_cycle.current_status == IllLoanCycle.STATUS_ON_LOAN, \
               'The ill loan cycle is in the wrong state'
    except AssertionError as e:
        exceptions.append(('ill', e))

    try:
        s = IllLoanCycle.STATUS_EXTENSION_REQUESTED
        msg = 'The ill loan cycle is in the wrong state'
        assert s in ill_loan_cycle.additional_statuses, msg
    except AssertionError as e:
        exceptions.append(('ill', e))

    try:
        assert ill_loan_cycle.desired_end_date is not None, \
                'A desired end date is necessary.'
    except AssertionError as e:
        exceptions.append(('ill', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def decline_ill_extension(ill_loan_cycle, reason=''):
    """Decline the requested extension for the given inter library loan.

    'extension_requested' will be removed from additional_statuses.
    The desired_end_date will be set to None.
    :raise: ValidationExceptions
    """
    try:
        try_decline_ill_extension(ill_loan_cycle)
    except ValidationExceptions as e:
        raise e

    ser = IllLoanCycle.STATUS_EXTENSION_REQUESTED
    ill_loan_cycle.desired_end_date = None
    ill_loan_cycle.additional_statuses.remove(ser)
    ill_loan_cycle.save()

    create_event(ill_loan_cycle_id=ill_loan_cycle.id,
                 event=IllLoanCycle.EVENT_ILL_CLC_EXTENSION_DECLINED,
                 description=reason)

    email_notification('ill_extension_request_declined', 'john.doe@cern.ch',
                       ill_loan_cycle.user.email,
                       loan_cycle=ill_loan_cycle)


def try_return_ill(ill_loan_cycle):
    """Check the conditions to return the inter library loan.

    Checked conditions:
    * The current_status must be 'on_loan'.

    :raise: ValidationExceptions
    """
    exceptions = []
    try:
        assert ill_loan_cycle.current_status == IllLoanCycle.STATUS_ON_LOAN, \
                'The ill loan cycle is in the wrong state'
    except AssertionError as e:
        exceptions.append(('ill', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def return_ill(ill_loan_cycle):
    """Return the given inter library loan.

    The ill_loan_cycles current_status will be set to 'finished'.
    The items current_status will be set to 'on_shelf'.

    This function should be called using a signal once the corresponding
    item is returned.

    :raise: ValidationExceptions
    """
    try:
        try_return_ill(ill_loan_cycle)
    except ValidationExceptions as e:
        raise e

    ill_loan_cycle.current_status = IllLoanCycle.STATUS_FINISHED
    ill_loan_cycle.save()

    ill_loan_cycle.item.current_status = CirculationItem.STATUS_ON_SHELF
    ill_loan_cycle.item.save()

    create_event(ill_loan_cycle_id=ill_loan_cycle.id,
                 event=IllLoanCycle.EVENT_ILL_CLC_FINISHED)


def try_send_back_ill(ill_loan_cycle):
    """Check the conditions to send the inter library loan back.

    Checked conditions:
    * The current_status must be 'finished'.

    :raise: ValidationExceptions
    """
    exceptions = []
    try:
        assert ill_loan_cycle.current_status == IllLoanCycle.STATUS_FINISHED, \
               'The ill loan cycle is in the wrong state'
    except AssertionError as e:
        exceptions.append(('ill', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def send_back_ill(ill_loan_cycle):
    """Send the given inter library loan back.

    The ill_loan_cycles current_status will be set to 'send_back'.
    The items current_status will be set to 'unavailable'.
    :raise: ValidationExceptions
    """
    try:
        try_send_back_ill(ill_loan_cycle)
    except ValidationExceptions as e:
        raise e

    ill_loan_cycle.current_status = IllLoanCycle.STATUS_SEND_BACK
    ill_loan_cycle.save()

    ill_loan_cycle.item.current_status = CirculationItem.STATUS_UNAVAILABLE
    ill_loan_cycle.item.save()

    create_event(ill_loan_cycle_id=ill_loan_cycle.id,
                 event=IllLoanCycle.EVENT_ILL_CLC_SEND_BACK)


def try_lose_ill(ill_loan_cycle):
    """Check the conditions to lose the inter library loan.

    Checked conditions:
    * The current_status must be 'on_loan'.

    :raise: ValidationExceptions
    """
    exceptions = []
    try:
        assert ill_loan_cycle.current_status == IllLoanCycle.STATUS_ON_LOAN, \
               'The ill loan cycle is in the wrong state'
    except AssertionError as e:
        exceptions.append(('ill', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def lose_ill(ill_loan_cycle):
    """Lose the given inter library loan.

    The ill_loan_cycles current_status will be set to 'missing'.
    The items current_status will be set to 'missing'.
    :raise: ValidationExceptions
    """
    try:
        try_lose_ill(ill_loan_cycle)
    except ValidationExceptions as e:
        raise e

    ill_loan_cycle.current_status = IllLoanCycle.STATUS_MISSING
    ill_loan_cycle.save()

    create_event(ill_loan_cycle_id=ill_loan_cycle.id,
                 event=IllLoanCycle.EVENT_ILL_CLC_LOST)

    lose_items([ill_loan_cycle.item])
