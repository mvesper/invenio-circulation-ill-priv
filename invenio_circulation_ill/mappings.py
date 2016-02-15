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

"""Module providing the elasticsearch mappings."""


def _add_copy_to(mappings):
    name = mappings['mappings'].keys()[0]
    full_text = {'type': 'string'}
    mappings['mappings'][name]['properties']['global_fulltext'] = full_text
    for key, value in mappings['mappings'][name]['properties'].items():
        try:
            value['copy_to'].append('global_fulltext')
        except AttributeError:
            value['copy_to'] = [value['copy_to'], 'global_fulltext']
        except KeyError:
            value['copy_to'] = ['global_fulltext']


ill_loan_cycle_mappings = {
        'mappings': {
            'ill_loan_cycle': {
                '_all': {'enabled': True},
                'properties': {
                    'id': {
                        'type': 'string',
                        'index': 'not_analyzed'},
                    'group_uuid': {
                        'type': 'string',
                        'index': 'not_analyzed'},
                    'end_date': {
                        'type': 'date', },
                    'global_fulltext': {
                        'type': 'string', },
                    }
                }
            }
        }
_add_copy_to(ill_loan_cycle_mappings)


ill_supplier_mappings = {
        'mappings': {
            'ill_supplier': {
                '_all': {'enabled': True},
                'properties': {
                    'id': {
                        'type': 'string',
                        'index': 'not_analyzed'},
                    'name': {
                        'type': 'string',
                        'index': 'not_analyzed',
                        'copy_to': 'content_ngram'},
                    'content_ngram': {'type': 'string',
                                      'term_vector': 'yes',
                                      'analyzer': 'trigrams'},
                    }
                }
            },
        'settings': {
            'analysis': {
                'filter': {
                    'trigrams_filter': {
                        'type': 'ngram',
                        'min_gram': 3,
                        'max_gram': 3
                        }
                    },
                'analyzer': {
                    'trigrams': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': [
                            'lowercase',
                            'trigrams_filter'
                            ]
                        }
                    }
                }
            }
        }

mappings = {'Ill Loan Cycle': ill_loan_cycle_mappings,
            'Ill Supplier': ill_supplier_mappings}
