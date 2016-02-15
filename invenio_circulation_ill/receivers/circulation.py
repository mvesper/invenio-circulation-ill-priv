from invenio_circulation.signals import (item_returned,
                                         circulation_other_actions)


def _item_returned(sender, data):
    import invenio_circulation_ill.models as models
    import invenio_circulation_ill.api as api

    item_id = data
    res = models.IllLoanCycle.search('item_id:{0}'.format(item_id))

    if res and len(res) == 1:
        api.ill.return_ill(res[0])
        return {'name': 'ill', 'result': True}

    return {'name': 'ill', 'result': None}


def _circulation_other_actions(sender, data):
    return {'name': 'ill', 'result': [('/circulation/ill/register_ill/',
                                       'Register ILL')]}


item_returned.connect(_item_returned)
circulation_other_actions.connect(_circulation_other_actions)
