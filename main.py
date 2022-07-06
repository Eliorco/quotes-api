import logging

from functools import reduce
from typing import List
from flask import Flask, request
from exchange_providers import (
    ExchangeProvider,
    ExchangerateProvider,
    FrankfurterProvider,
)


app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'SECRET_KEY'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # noqa
                    level=logging.INFO)
log = logging.getLogger(__name__)

# instead of redis or any DB that can keep count number of times provider provided
provider_balance_cnt = {
    'Exchangerate': 0,
    'Frankfurter': 0,
}

def get_provider(exchange_providers: List[ExchangeProvider]) -> ExchangeProvider:
    list_of_providers = [p for p in exchange_providers if p.rates.get(p.to)]
    log.info(f'Providers: {[p.name for p in list_of_providers]}')
    if not list_of_providers:
        raise Exception('No rates for picked currency, hint: check currency code')
    if len(list_of_providers) == 1:
        return list_of_providers[0]
    if not reduce(lambda x,y: x.amount == y.amount, list_of_providers):
        provider = max(list_of_providers)
    else:
        min_provider = min(provider_balance_cnt, key=provider_balance_cnt.get)
        provider = [p for p in list_of_providers if p.name == min_provider][0]
    return provider


def handle_request(_from: str, to: str, amount: int) -> dict:
    exchange_providers = [
        ExchangerateProvider(_from, to, amount),
        FrankfurterProvider(_from, to, amount)
    ]

    for provider in exchange_providers:
        provider.get_rate()

    try:
        best_provider = get_provider(exchange_providers)
    except Exception as e:
        log.error(str(e))
        return {'Error': str(e)}

    return {
        'exchange_rate': float('{:.3f}'.format(best_provider.rates[to])),
        'currency_code': best_provider._from,
        'amount': best_provider.amount,
        'provider_name': best_provider.name
    }

def query_param_parse_and_validate(args):
    args.to_dict()
    to_currency_code = args.get('to_currency_code')
    from_currency_code = args.get('from_currency_code')
    try:
        amount = int(args.get('amount',100))
    except Exception as e:
        raise Exception('"amount" field is an integer')

    if not all([from_currency_code, to_currency_code, amount]):
        raise Exception('Missing mendatory query params [from_currency_code, to_currency_code, amount] with valid value')
    if from_currency_code == to_currency_code:
        raise Exception('Please select two different currenct codes')

    return from_currency_code.upper(), to_currency_code.upper(), amount


@app.route("/api/quote")
def index():
    try:
        from_currency_code, to_currency_code, amount = query_param_parse_and_validate(
            request.args)
    except Exception as e:
        return {'Error': str(e)}

    resp = handle_request(from_currency_code, to_currency_code, amount)
    return resp

if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0', port=3000)