#! /usr/bin/env python


"""
    As part of this, I also installed
    eth-account
    eth-abi
    eth-utils
    websocket-client

"""

from hyperliquid.info import Info
from hyperliquid.utils import constants

import eth_account
import hyperliquid.utils as utils
from eth_account.signers.local import LocalAccount

from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants
import json
import os
import time
import sys


#info = Info(constants.MAINNET_API_URL)
info = Info(constants.TESTNET_API_URL)

my_wallet = "0x2AD7672c2990107b8Fd8130D896D5Bdd2aA4a6b9"
#user_state = info.user_state("0xcd5051944f780a621ee62e39e493c489668acf4d")

user_state = info.user_state(my_wallet)
#print(user_state)

# OK, cool. Next, now do I place an order?

def get_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path) as f:
        return json.load(f)


def try_order():
    config = get_config()

    account = eth_account.Account.from_key(config["secret_key"])
    print("Running with account address:", account.address)
    info = Info(constants.TESTNET_API_URL, skip_ws=True)

    # Get the user state and print out position information
    user_state = info.user_state(account.address)
    positions = []
    for position in user_state["assetPositions"]:
        if float(position["position"]["szi"]) != 0:
            positions.append(position["position"])
    if len(positions) > 0:
        print("positions:")
        for position in positions:
            print(json.dumps(position, indent=2))
    else:
        print("no open positions")

    tgt_coin = "SUSHI"
    tgt_px = 1.3
    tgt_qty = 10

    # Place an order that should rest by setting the price very low
    exchange = Exchange(account, constants.TESTNET_API_URL)
    print("Placing order: ")
    order_result = exchange.order("SUSHI", True, tgt_qty, tgt_px, {"limit": {"tif": "Gtc"}})
    print(order_result)

    # Normal order
    #{'status': 'ok', 'response': {'type': 'order', 'data': {'statuses': [{'resting': {'oid': 2745312460}}]}}}
    # Bad order (small size)
    # {'status': 'ok', 'response': {'type': 'order', 'data': {'statuses': [{'error': 'Order must have minimum value of $10.'}]}}}
    # Bad order (bad price)
    # {'status': 'ok', 'response': {'type': 'order', 'data': {'statuses': [{'error': 'Order has zero price.'}]}}}
    # Bad order (price precision wrong
    # # {'status': 'ok', 'response': {'type': 'order', 'data': {'statuses': [{'error': 'Order has invalid price.'}]}}}
    # Bad order (sz precision wrong)
    # {'status': 'ok', 'response': {'type': 'order', 'data': {'statuses': [{'error': 'Order has invalid size.'}]}}}

    # Execute.
    # {'status': 'ok', 'response': {'type': 'order', 'data': {'statuses': [{'filled': {'totalSz': '10.0', 'avgPx': '1.2852', 'oid': 2745613867}}]}}}

    return
    # Let's try to cancel the order too.
    order_id = order_result["response"]["data"]["statuses"][0]["resting"]["oid"]

    time.sleep(2.5)
    print("Cancelling order")
    cxl_result = exchange.cancel(tgt_coin, order_id)

    # {'status': 'ok', 'response': {'type': 'cancel', 'data': {'statuses': ['success']}}}
    print(cxl_result)



print("Hello world")
#try_order()



def dchen_place_order():
    config = get_config()

    account = eth_account.Account.from_key(config["secret_key"])
    print("Running with account address:", account.address)

    exchange = Exchange(account, constants.TESTNET_API_URL)
    tgt_coin = "SUSHI"
    tgt_px = 1.0
    tgt_qty = 10
    #order_result = exchange.order(tgt_coin, True, tgt_qty, tgt_px, {"limit": {"tif": "Gtc"}})

    # Unpacking everything

    # order = {'coin': 'SUSHI', 'is_buy': True, 'sz': 10, 'limit_px': 1.0, 'order_type': {'limit': {'tif': 'Gtc'}}, 'reduce_only': False}
    order_request = {'coin': 'SUSHI', 'is_buy': True, 'sz': 10, 'limit_px': 1.0, 'order_type': {'limit': {'tif': 'Gtc'}}, 'reduce_only': False}
    # This calls
    #order_request_to_order_spec
    # which creates
    # [{'order': {'asset': 63, 'isBuy': True, 'reduceOnly': False, 'limitPx': 1.0, 'sz': 10, 'cloid': None}, 'orderType': {'limit': {'tif': 'Gtc'}}}]

    # Then, gets the timestamp in ms and sets grouping to "na"

    # without cloid:
    #['(uint32,bool,uint64,uint64,bool,uint8,uint64)[]', 'uint8']
    # with cloid:
    #["(uint32,bool,uint64,uint64,bool,uint8,uint64,bytes16)[]", "uint8"]

    #Bunch of stuff gets passed into sign_l1_action
    # The post_action receives stuff like:
    # The order spec
    # ({'type': 'order', 'grouping': 'na', 'orders': [{'asset': 63, 'isBuy': True, 'limitPx': '1.00000000', 'sz': '10.00000000', 'reduceOnly': False, 'orderType': {'limit': {'tif': 'Gtc'}}, 'cloid': None}]},)
    # The signature
    # {'r': '0xf1479687acb259ebcfe33de36fb9d1c43a8102b45ab0619c16c6093116818c30', 's': '0x7531991921012fa51470995b97c4f408791ff413de19bcee846456fd421e0a6a', 'v': 27}
    # The timestamp
    # 1702057867083

    # OK, so now let's make sure we understand the sign_l1_action function
    # sign_l1_action gets:
    # wallet
    #<eth_account.signers.local.LocalAccount object at 0x7f929208ec80>
    # signature_types
    #['(uint32,bool,uint64,uint64,bool,uint8,uint64)[]', 'uint8']
    # signature_data
    #[[(63, True, 100000000, 1000000000, False, 2, 0)], 0]
    #active_pool (this is just the 0 address)
    #0x0000000000000000000000000000000000000000
    #nonce
    #1702058114094
    # is_mainnet
    #False

    # We then take the signature_data and append the ZERO_ADDRESS and then the nonce
    # [[(63, True, 100000000, 1000000000, False, 2, 0)], 0, '0x0000000000000000000000000000000000000000', 1702058305632]


    order_result = exchange.bulk_orders([order_request])

    order_id = order_result["response"]["data"]["statuses"][0]["resting"]["oid"]

    time.sleep(2.5)
    print("Cancelling order")
    cxl_result = exchange.cancel(tgt_coin, order_id)
    print(cxl_result)
    sys.exit()
    return



    # Place an order that should rest by setting the price very low
    print(order_result)

dchen_place_order()


# OK. Now I'm going to try to place an order, but break it all apart.


