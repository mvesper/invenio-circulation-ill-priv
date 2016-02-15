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

"""invenio-circulation-ill receiver to handle entity signals."""


from invenio_circulation.signals import (entities_overview,
                                         entities_hub_search,
                                         entity,
                                         entity_suggestions,
                                         entity_aggregations,
                                         entity_class,
                                         entity_name,
                                         entity_autocomplete_search,
                                         get_entity,
                                         save_entity)


def _entities_overview(sender, data):
    return {'name': 'ill_entity',
            'priority': 1.0,
            'result': [('ILL Loan Cycle', 'ill_loan_cycle'),
                       ('ILL Supplier', 'ill_supplier')]}


def _entities_hub_search(sender, data):
    import invenio_circulation_ill.models as models

    search = data

    models_entities = {'ill_loan_cycle': models.IllLoanCycle,
                       'ill_supplier': models.IllSupplier}

    entity = models_entities.get(sender)
    res = None
    if entity:
        res = (entity.search(search), 'ill_entities/' + sender + '.html')

    return {'name': 'ill_entity', 'result': res}


def _entity(sender, data):
    import invenio_circulation_ill.models as models

    id = data
    models_entities = {'ill_loan_cycle': models.IllLoanCycle,
                       'ill_supplier': models.IllSupplier}

    entity = models_entities.get(sender)
    res = entity.get(id) if entity else None

    return {'name': 'ill_entity', 'result': res}


def _entity_suggestions(entity, data):
    suggestions = {'ill_loan_cycle': [('item_id', 'item',
                                       ['id', 'record.title'],
                                      '/circulation/api/entity/search'),
                                      ('user_id', 'user',
                                       ['id', 'name'],
                                      '/circulation/api/entity/search')],
                   'ill_supplier': []}

    return {'name': 'ill_entity', 'result': suggestions.get(entity)}


def _entity_aggregations(entity, data):
    id = data

    res = None
    if entity == 'ill_loan_cycle':
        res = _get_loan_cycle_aggregations(id)

    return {'name': 'ill_entity', 'result': res}


def _get_loan_cycle_aggregations(id):
    import invenio_circulation.models as models
    import invenio_circulation_ill.models as ill_models

    from flask import render_template

    illc = ill_models.IllLoanCycle.get(id)

    items = [illc.item]
    users = [illc.user]
    events = models.CirculationEvent.search('ill_loan_cycle_id:{0}'.format(id))
    events = sorted(events, key=lambda x: x.creation_date)

    return [render_template('aggregations/user.html', users=users),
            render_template('aggregations/item.html', items=items),
            render_template('aggregations/event.html', events=events)]


def _entity_class(entity, data):
    import invenio_circulation_ill.models as models

    models = {'ill_loan_cycle': models.IllLoanCycle,
              'ill_supplier': models.IllSupplier}

    return {'name': 'ill_entity', 'result': models.get(entity)}


def _entity_name(entity, data):
    names = {'ill_loan_cycle': 'Ill Loan Cycle',
             'ill_supplier': 'Ill Supplier'}

    return {'name': 'ill_entity', 'result': names.get(entity)}


def _get_entity(class_name, data):
    class_names = {'CirculationEvent': ['ill_loan_cycle_id']}
    return {'name': 'ill', 'result': class_names.get(class_name)}


def _save_entity(class_name, data):
    class_names = {'CirculationEvent': ['ill_loan_cycle_id']}
    return {'name': 'ill', 'result': class_names.get(class_name)}


def _entity_autocomplete_search(entity, data):
    import invenio_circulation_ill.models as models

    q = {'query': {'bool': {'should': {'match': {'content_ngram': data}}}}}
    res = None
    if entity == 'ill_supplier':
        res = models.IllSupplier._es.search(
                index=models.IllSupplier.__tablename__, body=q)
        res = [models.IllSupplier.get(x['_id']) for x in res['hits']['hits']]
        res = [{'id': x.id, 'value': x.name} for x in res]

    return {'name': 'ill', 'result': res}


entities_overview.connect(_entities_overview)
entities_hub_search.connect(_entities_hub_search)
entity.connect(_entity)
entity_suggestions.connect(_entity_suggestions)
entity_aggregations.connect(_entity_aggregations)
entity_class.connect(_entity_class)
entity_name.connect(_entity_name)
entity_autocomplete_search.connect(_entity_autocomplete_search)
get_entity.connect(_get_entity)
save_entity.connect(_save_entity)
