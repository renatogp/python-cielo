import unittest
from decimal import Decimal
from cielo import GetAuthorizedException, PaymentAttempt, CreditCardToken


class MainTest(unittest.TestCase):
    def test_payment_attempt_authorized(self):
        params = {
            'affiliation_id': '1006993069',
            'api_key': '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3',
            'card_type': PaymentAttempt.VISA,
            'total': Decimal('1.00'),  # when amount ends with .00 attempt is automatically authorized
            'order_id': '7DSD163AH1',  # strings are allowed here
            'card_number': '4012001037141112',
            'cvc2': 423,
            'exp_month': 1,
            'exp_year': 2010,
            'card_holders_name': 'JOAO DA SILVA',
            'installments': 1,
            'transaction': PaymentAttempt.CASH,
            'sandbox': True,
        }

        attempt = PaymentAttempt(**params)
        self.assertTrue(attempt.get_authorized())

    def test_payment_attempt_unauthorized(self):
        params = {
            'affiliation_id': '1006993069',
            'api_key': '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3',
            'card_type': PaymentAttempt.VISA,
            'total': Decimal('1.01'),  # when amount does not end with .00 attempt is automatically cancelled
            'order_id': '7DSD63A1H1',  # strings are allowed here
            'card_number': '4012001037141112',
            'cvc2': 423,
            'exp_month': 1,
            'exp_year': 2010,
            'card_holders_name': 'JOAO DA SILVA',
            'installments': 1,
            'transaction': PaymentAttempt.CASH,
            'sandbox': True,
        }

        attempt = PaymentAttempt(**params)
        self.assertRaises(GetAuthorizedException, attempt.get_authorized)

    def test_payment_attempt_capture(self):
        params = {
            'affiliation_id': '1006993069',
            'api_key': '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3',
            'card_type': PaymentAttempt.VISA,
            'total': Decimal('1.00'),  # when amount ends with .00 attempt is automatically authorized
            'order_id': '7DSD163AH1',  # strings are allowed here
            'card_number': '4012001037141112',
            'cvc2': 423,
            'exp_month': 1,
            'exp_year': 2010,
            'card_holders_name': 'JOAO DA SILVA',
            'installments': 1,
            'transaction': PaymentAttempt.CASH,
            'sandbox': True,
        }

        attempt = PaymentAttempt(**params)
        self.assertTrue(attempt.get_authorized())
        self.assertTrue(attempt.capture())
        # self.assertRaises(GetAuthorizedException, attempt.get_authorized)

    def test_credit_card_token_creation(self):
        params = {
            'affiliation_id': '1006993069',
            'api_key': '25fbb99741c739dd84d7b06ec78c9bac718838630f30b112d033ce2e621b34f3',
            'card_number': '4012001037141112',
            'exp_month': 1,
            'exp_year': 2010,
            'card_holders_name': 'JOAO DA SILVA',
            'sandbox': True,
        }

        cc_token = CreditCardToken(**params)
        self.assertEqual(cc_token.create(), {
            'token': 'O/sN7IgUNo4FKXy6SeQRc+BbuZiFvYo4Sqdph0EWaoI=',
            'truncated': '401200******1112',
        })

if __name__ == '__main__':
    unittest.main()
