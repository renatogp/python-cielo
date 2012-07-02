# coding: utf-8
from datetime import datetime
import os
import requests
import xml.dom.minidom
from decimal import Decimal
from util import moneyfmt


SANDBOX_URL = 'https://qasecommerce.cielo.com.br/servicos/ecommwsec.do'
PRODUCTION_URL = 'https://ecommerce.cbmp.com.br/servicos/ecommwsec.do'


class GetAuthorizedException(Exception):
    def __init__(self, id, message=None):
        self.id = id
        self.message = message

    def __str__(self):
        return u'%s - %s' % (self.id, self.message)


class CaptureException(Exception):
    pass


class PaymentAttempt(object):
    VISA, MASTERCARD, DINERS, DISCOVER, ELO, AMEX = 'visa', 'mastercard', 'diners', 'discover', 'elo', 'amex'
    CARD_TYPE_C = (
        (VISA, u'Visa'),
        (MASTERCARD, u'Mastercard'),
        (DINERS, u'Diners'),
        (DISCOVER, u'Discover'),
        (ELO, u'ELO'),
        (AMEX, u'American express'),
    )

    CASH, INSTALLMENT_STORE, INSTALLMENT_CIELO = 1, 2, 3
    TRANSACTION_TYPE_C = (
        (CASH, u'À vista'),
        (INSTALLMENT_STORE, u'Parcelado (estabelecimento)'),
        (INSTALLMENT_CIELO, u'Parcelado (Cielo)'),
    )

    def __init__(self, affiliation_id, api_key, total, card_type, installments, order_id, card_number, cvc2,
                exp_month, exp_year, card_holders_name, transaction=CASH, sandbox=False):

        assert isinstance(total, Decimal), u'total must be an instance of Decimal'
        assert installments in range(1, 13), u'installments must be a integer between 1 and 12'

        assert (installments == 1 and transaction == self.CASH) \
                    or installments > 1 and transaction != self.CASH, \
                    u'if installments = 1 then transaction must be None or "cash"'

        if len(str(exp_year)) == 2:
            exp_year = '20%s' % exp_year  # FIXME: bug do milênio em 2100

        self.url = SANDBOX_URL if sandbox else PRODUCTION_URL
        self.card_type = card_type
        self.affiliation_id = affiliation_id
        self.api_key = api_key
        self.transaction = transaction
        self.transaction_type = transaction  # para manter assinatura do pyrcws
        self.total = moneyfmt(total, sep='', dp='')
        self.installments = installments
        self.order_id = order_id
        self.card_number = card_number
        self.cvc2 = cvc2
        self.exp_month = exp_month
        self.exp_year = exp_year
        self.expiration = '%s%s' % (exp_year, exp_month)
        self.card_holders_name = card_holders_name
        self._authorized = False

    def get_authorized(self):
        self.date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        payload = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'authorize.xml'), 'r').read() % self.__dict__

        response = requests.post(self.url, data={
            'mensagem': payload,
        })

        dom = xml.dom.minidom.parseString(response.content)

        if dom.getElementsByTagName('erro'):
            error_id = dom.getElementsByTagName('codigo')[0].childNodes[0].data
            error_message = dom.getElementsByTagName('mensagem')[0].childNodes[0].data
            raise GetAuthorizedException(error_id, error_message)

        status = int(dom.getElementsByTagName('status')[0].childNodes[0].data)
        if status != 4:
            # 4 = autorizado (ou captura pendente)
            self._authorized = False
            raise GetAuthorizedException(status)

        self.transaction_id = dom.getElementsByTagName('tid')[0].childNodes[0].data
        self.pan = dom.getElementsByTagName('pan')[0].childNodes[0].data

        self._authorized = True
        return True

    def capture(self):
        assert self._authorized, u'get_authorized(...) must be called before capture(...)'

        payload = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'capture.xml'), 'r').read() % self.__dict__

        response = requests.post(self.url, data={
            'mensagem': payload,
        })

        dom = xml.dom.minidom.parseString(response.content)
        status = int(dom.getElementsByTagName('status')[0].childNodes[0].data)

        if status != 6:
            # 6 = capturado
            raise CaptureException()
        return True

