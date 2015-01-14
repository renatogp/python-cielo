============
python-cielo
============

python-cielo is a lightweight lib for making payments over the Cielo webservice (Brazil)

Installation
^^^^^^^^^^^^^
Use ``PIP`` or ``easy_install``: ::

    pip install -e git+git://github.com/guilhermetavares/python-cielo.git#egg=python-cielo

Usage
^^^^^

Cielo ``key`` and ``affiliation``: ::

    CIELO_API_KEY = '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3'
    CIELO_AFFILIATION_ID = '1006993069'


For send a simple transaction: ::

    from cielo import PaymentAttempt, CASH, VISA
    from decimal import Decimal

    params = {
            'affiliation_id': CIELO_AFFILIATION_ID,
            'api_key': CIELO_API_KEY,
            'card_type': VISA,
            'total': Decimal('1.00'),  # when amount ends with .00 attempt is automatically authorized
            'order_id': '7DSD163AH1',  # strings are allowed here
            'card_number': '4012001037141112',
            'cvc2': 423,
            'exp_month': 1,
            'exp_year': 2010,
            'card_holders_name': 'JOAO DA SILVA',
            'installments': 1,
            'transaction': CASH,
            'sandbox': True,
            'use_ssl': None # if is None, will be considered the opposite of sandbox.
        }
    attempt = PaymentAttempt(**params)
    attempt.get_authorized()
    attempt.capture()


Tests
^^^^^
For tests: ::

    python tests.py


Documentation
^^^^^^^^^^^^^
Docs are hosted at `ReadTheDocs <http://python-cielo.readthedocs.org/>`_.
