import unittest
from decimal import Decimal
from cielo import *


class MainTest(unittest.TestCase):

    def test_01_payment_attempt_authorized(self):
        params = {
            'affiliation_id': '1006993069',
            'api_key': '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3',
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
        }

        attempt = PaymentAttempt(**params)
        self.assertTrue(attempt.get_authorized())

    def test_02_payment_attempt_unauthorized(self):
        params = {
            'affiliation_id': '1006993069',
            'api_key': '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3',
            'card_type': VISA,
            'total': Decimal('1.01'),  # when amount does not end with .00 attempt is automatically cancelled
            'order_id': '7DSD63A1H1',  # strings are allowed here
            'card_number': '4012001037141112',
            'cvc2': 423,
            'exp_month': 1,
            'exp_year': 2010,
            'card_holders_name': 'JOAO DA SILVA',
            'installments': 1,
            'transaction': CASH,
            'sandbox': True,
        }

        attempt = PaymentAttempt(**params)
        self.assertRaises(GetAuthorizedException, attempt.get_authorized)

    def test_03_payment_attempt_capture(self):
        params = {
            'affiliation_id': '1006993069',
            'api_key': '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3',
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
        }

        attempt = PaymentAttempt(**params)
        self.assertTrue(attempt.get_authorized())
        self.assertTrue(attempt.capture())

    def test_04_create_cielo_token(self):
        params = {
            'affiliation_id': '1006993069',
            'api_key': '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3',
            'card_type': 'visa',
            'card_number': '4012001037141112',
            'exp_month': 1,
            'exp_year': 2010,
            'card_holders_name': 'JOAO DA SILVA',
            'sandbox': True,
        }
        token = CieloToken(**params)
        token.create_token()
        self.assertEqual(token.status, '1')
        self.assertTrue('1112' in token.card)

    def test_05_raises_create_cielo_token(self):
        params = {
            'affiliation_id': '323298379',
            'api_key': '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3',
            'card_type': 'visa',
            'card_number': '4012001037141112',
            'exp_month': 1,
            'exp_year': 2010,
            'card_holders_name': 'JOAO DA SILVA',
            'sandbox': True,
        }
        token = CieloToken(**params)
        self.assertRaises(TokenException, token.create_token)

    def test_06_token_payment_attempt(self):
        params = {
            'affiliation_id': '1006993069',
            'api_key': '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3',
            'card_type': 'visa',
            'card_number': '4012001037141112',
            'exp_month': 1,
            'exp_year': 2010,
            'card_holders_name': 'JOAO DA SILVA',
            'sandbox': True,
        }
        token = CieloToken(**params)
        token.create_token()
        self.assertEqual(token.status, '1')
        self.assertTrue('1112' in token.card)

        params = {
            'affiliation_id': token.affiliation_id,
            'api_key': token.api_key,
            'card_type': token.card_type,
            'total': Decimal('1.00'),
            'order_id': '7DSD163AH1',
            'token': token.token,
            'installments': 1,
            'transaction': CASH,
            'sandbox': token.sandbox,
            'url_redirect': 'http://127.0.0.1:8000/',
        }
        attempt = TokenPaymentAttempt(**params)
        self.assertTrue(attempt.get_authorized())
        self.assertTrue(attempt.capture())

    def test_07_payment_canceled(self):
        params = {
            'affiliation_id': '1006993069',
            'api_key': '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3',
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
        }

        attempt = PaymentAttempt(**params)
        self.assertTrue(attempt.get_authorized())
        self.assertTrue(attempt.capture())

        cancel_params = {
            'sandbox': True,
            'transaction_id': attempt.transaction_id,
            'affiliation_id': '1006993069',
            'api_key': '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3',
            'amount_to_cancel': '1.00',
        }
        self.assertRaises(AssertionError, CancelTransaction, **cancel_params)

        cancel_params = {
            'sandbox': True,
            'transaction_id': attempt.transaction_id,
            'affiliation_id': '1006993069',
            'api_key': '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3',
            'amount_to_cancel': Decimal('1.00'),
        }

        cancel = CancelTransaction(**cancel_params)
        self.assertTrue(cancel.cancel())

if __name__ == '__main__':
    unittest.main()
