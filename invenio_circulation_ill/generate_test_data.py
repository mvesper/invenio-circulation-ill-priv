def create_indices(app):
    from invenio_circulation_ill.models import entities
    from invenio_circulation_ill.mappings import mappings

    for name, _, cls in filter(lambda x: x[0] != 'Record', entities):
        mapping = mappings.get(name, {})
        index = cls.__tablename__
        cls._es.indices.delete(index=index, ignore=404)
        cls._es.indices.create(index=index, body=mapping)


def generate(app=None):
    import datetime

    import invenio_circulation.models as models
    import invenio_circulation_ill.models as ill_models
    import invenio_circulation_ill.api as api

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
