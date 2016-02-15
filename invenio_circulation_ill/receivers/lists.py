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
