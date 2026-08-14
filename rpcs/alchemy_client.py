import time

import requests

from utils.timing import io_timer
from utils.utils import (
    CustomException,
    convert_blockchain_into_alchemy_id,
    load_alchemy_api_key,
    log_error,
)


class AlchemyClient:
    CLASS_NAME = "AlchemyClient"

    @staticmethod
    def get_token_metadata(blockchain: str, contract: str) -> dict:
        func_name = "get_token_metadata"

        with io_timer.track("pricing"):
            blockchain_id = convert_blockchain_into_alchemy_id(blockchain)

            url = f"https://{blockchain_id}-mainnet.g.alchemy.com/v2/{load_alchemy_api_key()}/"

            payload = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "alchemy_getTokenMetadata",
                "params": [contract],
            }
            headers = {"accept": "application/json", "content-type": "application/json"}

            response = requests.post(url, json=payload, headers=headers)

            if response.status_code != 200:
                raise CustomException(
                    AlchemyClient.CLASS_NAME,
                    func_name,
                    f"Alchemy request failed with status code {response.status_code}",
                )

            return response.json()["result"] if response else {}

    @staticmethod
    def get_token_prices_by_symbol_or_address(
        bridge: str,
        start_ts: int,
        end_ts: int,
        symbol: str = None,
        blockchain: str = None,
        token_address: str = None,
    ) -> dict:
        func_name = "get_token_prices_by_symbol_or_address"

        with io_timer.track("pricing"):
            payload = {}

            if not symbol:
                if blockchain is None or token_address is None:
                    raise CustomException(
                        AlchemyClient.CLASS_NAME,
                        func_name,
                        "Either symbol or blockchain and token_address must be provided.",
                    )

                blockchain_id = convert_blockchain_into_alchemy_id(blockchain)

                if blockchain_id is None:
                    return {}

                payload = {
                    "network": f"{blockchain_id}-mainnet",
                    "address": token_address,
                    "startTime": start_ts,
                    "endTime": end_ts,
                    "interval": "1d",
                }
            else:
                if blockchain is not None or token_address is not None:
                    raise CustomException(
                        AlchemyClient.CLASS_NAME,
                        func_name,
                        "Either symbol or blockchain and token_address must be provided.",
                    )

                payload = {
                    "symbol": symbol,
                    "startTime": start_ts,
                    "endTime": end_ts,
                    "interval": "1d",
                }

            url = f"https://api.g.alchemy.com/prices/v1/{load_alchemy_api_key()}/tokens/historical"

            headers = {
                "accept": "application/json",
                "content-type": "application/json",
            }

            response = requests.post(url, json=payload, headers=headers)

            for i in range(5):
                try:
                    response = requests.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    return response.json() if response else {}
                except requests.exceptions.RequestException:
                    # if response.text contains "token not found" return {}
                    if "Token not found" in response.text:
                        return {}

                    exception = CustomException(
                        AlchemyClient.CLASS_NAME,
                        func_name,
                        (
                            f"Fetching token price with payload: {payload} "
                            f"failed with error: {response.text}",
                        ),
                    )

                    log_error(bridge, exception)

                    if "Your free app has exceeded its limit" in response.text:
                        # If the error is due to rate limiting, return an empty dict
                        # The tool will continue to run and fetch metadata for other tokens,
                        # as the rate limit is only for token price fetching
                        return {}

                    if i < 4:
                        time.sleep(2**i)  # Exponential backoff
                    else:
                        return None

            return response.json() if response else {}
