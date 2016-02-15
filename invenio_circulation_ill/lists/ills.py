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


class RequestedIlls(BaseIlls):
    current_status = models.IllLoanCycle.STATUS_REQUESTED
    positive_actions = [('confirm', 'CONFIRM')]
    negative_actions = [('decline', 'DECLINE')]


class OrderedIlls(BaseIlls):
    current_status = models.IllLoanCycle.STATUS_ORDERED
    positive_actions = [('deliver', 'DELIVER')]
    negative_actions = [('cancel', 'CANCEL')]


class LoanedIlls(BaseIlls):
    current_status = models.IllLoanCycle.STATUS_ON_LOAN
    negative_actions = [('return', 'RETURN')]


class CanceledIlls(BaseIlls):
    current_status = models.IllLoanCycle.STATUS_CANCELED


class ReturnedIlls(BaseIlls):
    current_status = models.IllLoanCycle.STATUS_FINISHED


class ExtensionIlls(object):
    @classmethod
    def entrance(cls):
        positive_actions = [('confirm_ill_extension', 'CONFIRM')]
        negative_actions = [('decline_ill_extension', 'DECLINE')]
        s = models.IllLoanCycle.STATUS_EXTENSION_REQUESTED
        q = 'additional_statuses:{0}'.format(s)
        ill_clcs = models.IllLoanCycle.search(q)
        return render_template('lists/base_ills.html', ill_clcs=ill_clcs,
                               active_nav='lists',
                               positive_actions=positive_actions,
                               negative_actions=negative_actions)
