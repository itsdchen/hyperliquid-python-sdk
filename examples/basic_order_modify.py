import json

import eth_account
import utils
from eth_account.signers.local import LocalAccount

from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants


def main():
    config = utils.get_config()
    account: LocalAccount = eth_account.Account.from_key(config["secret_key"])
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

    # Place an order that should rest by setting the price very low
    exchange = Exchange(account, constants.TESTNET_API_URL)
    order_result = exchange.order("ETH", True, 0.2, 1100, {"limit": {"tif": "Gtc"}})
    print(order_result)

    # Modify the order by oid
    if order_result["status"] == "ok":
        status = order_result["response"]["data"]["statuses"][0]
        if "resting" in status:
            oid = status["resting"]["oid"]
            order_status = info.query_order_by_oid(account.address, oid)
            print("Order status by oid:", order_status)

            modify_result = exchange.modify_order(oid, "ETH", True, 0.1, 1105, {"limit": {"tif": "Gtc"}})
            print("modify result:", modify_result)


if __name__ == "__main__":
    main()
