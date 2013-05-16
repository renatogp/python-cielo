# coding: utf-8
from datetime import datetime
import os
import requests
import xml.dom.minidom
from decimal import Decimal
from util import moneyfmt


SANDBOX_URL = 'https://qasecommerce.cielo.com.br/servicos/ecommwsec.do'
PRODUCTION_URL = 'https://ecommerce.cbmp.com.br/servicos/ecommwsec.do'
CIELO_MSG_ERRORS = {
    '001': u'A mensagem XML está fora do formato especificado pelo arquivo ecommerce.xsd (001-Mensagem inválida)',
    '002': u'Impossibilidade de autenticar uma requisição da loja virtual. (002-Credenciais inválidas)',
    '003': u'Não existe transação para o identificador informado. (003-Transação inexistente)',
    '010': u'A transação, com ou sem cartão, está divergente com a permissão do envio dessa informação. (010-Inconsistência no envio do cartão)',
    '011': u'A transação está configurada com uma modalidade de pagamento não habilitada para a loja. (011-Modalidade não habilitada)',
    '012': u'O número de parcelas solicitado ultrapassa o máximo permitido. (012-Número de parcelas inválido)',
    '020': u'Não é permitido realizar autorização para o status da transação. (020-Status não permite autorização)',
    '021': u'Não é permitido realizar autorização, pois o prazo está vencido. (021-Prazo de autorização vencido)',
    '022': u'EC não possui permissão para realizar a autorização.(022-EC não autorizado)',
    '030': u'A captura não pode ser realizada, pois a transação não está autorizada.(030-Transação não autorizada para captura)',
    '031': u'A captura não pode ser realizada, pois o prazo para captura está vencido.(031-Prazo de captura vencido)',
    '032': u'O valor solicitado para captura não é válido.(032-Valor de captura inválido)',
    '033': u'Não foi possível realizar a captura.(033-Falha ao capturar)',
    '040': u'O cancelamento não pode ser realizado, pois o prazo está vencido.(040-Prazo de cancelamento vencido)',
    '041': u'O atual status da transação não permite cancelament.(041-Status não permite cancelamento)',
    '042': u'Não foi possível realizar o cancelamento.(042-Falha ao cancelar)',
    '099': u'Falha no sistema.(099-Erro inesperado)',
}


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

        self.sandbox = sandbox

    def get_authorized(self):
        self.date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        self.payload = open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'authorize.xml'), 'r').read() % self.__dict__

        self.response = requests.post(
            self.url,
            data={'mensagem': self.payload, })

        self.dom = xml.dom.minidom.parseString(self.response.content)

        if self.dom.getElementsByTagName('erro'):
            self.error_id = self.dom.getElementsByTagName(
                'erro')[0].getElementsByTagName('codigo')[0].childNodes[0].data
            try:
                self.error_message = CIELO_MSG_ERRORS[self.error_id]
            except IndexError:
                self.error_message = u'Erro não especificado, ver documentação (código %s)' % self.error_id
            raise GetAuthorizedException(self.error_id, self.error_message)

        self.status = int(
            self.dom.getElementsByTagName('status')[0].childNodes[0].data)
        if self.status != 4:
            self.error_id = self.dom.getElementsByTagName(
                'autorizacao')[0].getElementsByTagName(
                    'codigo')[0].childNodes[0].data
            self.error_message = self.dom.getElementsByTagName(
                'autorizacao')[0].getElementsByTagName(
                    'mensagem')[0].childNodes[0].data
            self._authorized = False
            raise GetAuthorizedException(self.error_id, self.error_message)

        self.transaction_id = self.dom.getElementsByTagName(
            'tid')[0].childNodes[0].data
        self.pan = self.dom.getElementsByTagName('pan')[0].childNodes[0].data

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
