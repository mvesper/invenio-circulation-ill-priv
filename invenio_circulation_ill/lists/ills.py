import json
import invenio_circulation_ill.models as models

from flask import render_template


class BaseIlls(object):
    positive_actions = None
    negative_actions = None

    @classmethod
    def entrance(cls):
        q = 'current_status:{0}'.format(cls.current_status)
        ill_clcs = models.IllLoanCycle.search(q)
        return render_template('lists/base_ills.html', ill_clcs=ill_clcs,
                               active_nav='lists',
                               positive_actions=cls.positive_actions,
                               negative_actions=cls.negative_actions)

    @classmethod
    def data(cls):
        q = 'current_status:{0}'.format(cls.current_status)
        return [{'id': x.id,
                 'item': cls._make(x),
                 'type': cls.type,
                 'positive_actions': cls.positive_actions,
                 'negative_actions': cls.negative_actions}
                for x in  models.IllLoanCycle.search(q)]

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
    table_header = ['Borrower', 'CCID', 'Record', 'Start Date', 'End Date']
    item_accessors = ['user.name', 'user.ccid', 'item.record.title',
                      'start_date', 'end_date']
    type = 'Ill Request'
    current_status = models.IllLoanCycle.STATUS_REQUESTED
    positive_actions = [('confirm_ill_request', 'CONFIRM', 'ill_confirmation')]
    negative_actions = [('decline_ill_request', 'DECLINE')]


class OrderedIlls(BaseIlls):
    current_status = models.IllLoanCycle.STATUS_ORDERED
    positive_actions = [('deliver_ill', 'DELIVER', None)]
    negative_actions = [('cancel_ill_request', 'CANCEL')]


class LoanedIlls(BaseIlls):
    current_status = models.IllLoanCycle.STATUS_ON_LOAN
    positive_actions = [('return_ill', 'RETURN', None)]


class CanceledIlls(BaseIlls):
    current_status = models.IllLoanCycle.STATUS_CANCELED


class ReturnedIlls(BaseIlls):
    current_status = models.IllLoanCycle.STATUS_FINISHED


class ExtensionIlls(object):
    @classmethod
    def entrance(cls):
        positive_actions = [('confirm_ill_extension', 'CONFIRM', None)]
        negative_actions = [('decline_ill_extension', 'DECLINE')]
        s = models.IllLoanCycle.STATUS_EXTENSION_REQUESTED
        q = 'additional_statuses:{0}'.format(s)
        ill_clcs = models.IllLoanCycle.search(q)
        return render_template('lists/extension_ills.html', ill_clcs=ill_clcs,
                               active_nav='lists',
                               positive_actions=positive_actions,
                               negative_actions=negative_actions)
