.. python-cielo documentation master file, created by
   sphinx-quickstart on Tue Jun 19 18:10:31 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

python-cielo
============

=========================
Para uma transação normal
=========================

Biblioteca para autorização e captura de pagamentos pelo webservice da Cielo.

Autorização e captura
---------------------

Para efetuar uma transação utilize o seguinte modelo: ::

    from decimal import Decimal
    from cielo import PaymentAttempt, GetAuthorizedException, VISA, CASH

    params = {
        'affiliation_id': '1234567890',
        'api_key': 'ABCDEFG123456789',
        'card_type': VISA,
        'total': Decimal('1.00'),
        'order_id': '7DSD163AH1',  # strings são permitidas
        'card_number': '4012001037141112',
        'cvc2': 423,  # código de segurança
        'exp_month': 1,
        'exp_year': 2010,
        'transaction': CASH,
        'card_holders_name': 'JOAO DA SILVA',
        'installments': 1,
    }

    attempt = PaymentAttempt(**params)
    try:
        attempt.get_authorized()
    except GetAuthorizedException, e:
        print u'Não foi possível processar: %s' % e
    else:
        attempt.capture()


Parâmetros
^^^^^^^^^^
Verifique abaixo a lista de parâmetros esperados no construtor da classe ``PaymentAttempt``.

==========================  ===============================================  ======================================
Atributo                    Descrição                                        Observações
==========================  ===============================================  ======================================
``affiliation_id``          Número de afiliação junto à Cielo
``api_key``                 Chave de acesso para o webservice
``card_type``               Bandeira do cartão                               Veja as bandeiras suportadas
``total``                   Valor total do pedido (utilizar ``Decimal``)
``order_id``                Identificador único do pedido
``card_number``             Número do cartão (sem pontos)
``cvc2``                    Código de segurança
``exp_month``               Mês de vencimento
``exp_year``                Ano de vencimento
``card_holders_name``       Nome impresso no cartão
``installments``            Número de parcelas
``transaction``             Tipo da transação / parcelamento                 Veja os tipos de transações suportados
``sandbox``                 Ambiente de desenvolvimento                      Default: ``False``
==========================  ===============================================  ======================================


============================
Para uma transação via token
============================

Gerando um novo token
---------------------

Para criar um novo token junto a Cielo: ::

    from cielo import CieloToken, VISA

    params = {
        'affiliation_id': '1234567890',
        'api_key': 'ABCDEFG123456789',
        'card_type': VISA,
        'card_number': '4012001037141112',
        'exp_month': 1,
        'exp_year': 2010,
        'card_holders_name': 'JOAO DA SILVA',
        'sandbox': True,
    }

    cielo_token = CieloToken(**params)
    cielo_token.create_token()

Autorização e captura com token
-------------------------------

A partir da instancia CieloToken como variável ``cielo_token``: ::

    from cielo import TokenPaymentAttempt, CASH

    params = {
        'affiliation_id': '1234567890',
        'api_key': 'ABCDEFG123456789',
        'card_type': cielo_token.card_type,
        'transaction': CASH,
        'total': Decimal('1.00'),
        'order_id': '7DSD163AH1',
        'installments': 1,
        'token': cielo_token.token,
        'sandbox': True,
        'url_redirect': 'http://localhost:8000/',
    }

    attempt = TokenPaymentAttempt(**params)
    try:
        attempt.get_authorized()
    except GetAuthorizedException, e:
        print u'Não foi possível processar: %s' % e
    else:
        attempt.capture()

Parâmetros
^^^^^^^^^^
Verifique abaixo a lista de parâmetros esperados no construtor da classe ``CieloToken``.

==========================  ===============================================  ======================================
Atributo                    Descrição                                        Observações
==========================  ===============================================  ======================================
``affiliation_id``          Número de afiliação junto à Cielo
``api_key``                 Chave de acesso para o webservice
``card_type``               Bandeira do cartão                               Veja as bandeiras suportadas
``card_number``             Número do cartão (sem pontos)
``exp_month``               Mês de vencimento
``exp_year``                Ano de vencimento
``card_holders_name``       Nome impresso no cartão
``sandbox``                 Ambiente de desenvolvimento                      Default: ``False``
==========================  ===============================================  ======================================

Verifique abaixo a lista de parâmetros esperados no construtor da classe ``TokenPaymentAttempt``.

==========================  ===============================================  ======================================
Atributo                    Descrição                                        Observações
==========================  ===============================================  ======================================
``affiliation_id``          Número de afiliação junto à Cielo
``api_key``                 Chave de acesso para o webservice
``card_type``               Bandeira do cartão                               Veja as bandeiras suportadas
``total``                   Valor total do pedido (utilizar ``Decimal``)
``token``                   Token gerado pela Cielo
``url_redirect``            URL para redirecionamento
``order_id``                Identificador único do pedido
``installments``            Número de parcelas
``transaction``             Tipo da transação / parcelamento                 Veja os tipos de transações suportados
``sandbox``                 Ambiente de desenvolvimento                      Default: ``False``
==========================  ===============================================  ======================================

Bandeiras suportadas
^^^^^^^^^^^^^^^^^^^^
Atualmente as seguintes bandeiras são suportadas:

* Visa: ``PaymentAttempt.VISA``
* Mastercard: ``PaymentAttempt.MASTERCARD``
* Diners: ``PaymentAttempt.DINERS``
* Discover: ``PaymentAttempt.DISCOVER``
* ELO: ``PaymentAttempt.ELO``
* American express: ``PaymentAttempt.AMEX``


Tipos de transações
^^^^^^^^^^^^^^^^^^^
Atualmente os seguintes tipos de transações são suportados:

* À vista (uma parcela): ``PaymentAttempt.CASH``
* Parcelado pelo estabelecimento: ``PaymentAttempt.INSTALLMENT_STORE``
* Parcelado pela emissora: ``PaymentAttempt.INSTALLMENT_CIELO``

.. warning::
    Antes de iniciar as vendas, verifique as taxas de cada tipo de transação junto à Cielo.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

