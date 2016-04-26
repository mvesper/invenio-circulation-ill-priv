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

"""Development helper module to generate very basic test data."""


def create_indices(app):
    """Create the indices for invenio-circulation-ill.

    Iterates over every entity in invenio_ciruclation-ill.models.entities and
    creates the corresponding index.

    :param app: [A/The current] Flask application.
    """
    from invenio_circulation_ill.models import entities
    from invenio_circulation_ill.mappings import mappings

    for name, _, cls in filter(lambda x: x[0] != 'Record', entities):
        mapping = mappings.get(name, {})
        index = cls.__tablename__
        cls._es.indices.delete(index=index, ignore=404)
        cls._es.indices.create(index=index, body=mapping)


def generate(app=None):
    """Generate indices and test entities.

    :param app: [A/The current] Flask application.
    """
    import invenio_circulation_ill.models as ill_models

    create_indices(app)

    ill_models.IllSupplier.new(name='Amazon.com')
    ill_models.IllSupplier.new(name='Amazon.fr')
    ill_models.IllSupplier.new(name='Amazon.co.uk')

    '''
    user = models.CirculationUser.get(1)
    record = models.CirculationRecord.get_all()[0]

    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(weeks=4)

    api.ill.request_ill(user, record, start_date, end_date)
    '''
