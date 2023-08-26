from config import Crypto_API_TESTNET
from requests import post
import random

def transfer(price: float, to_id: int) -> None:
    headers = {'Crypto-Pay-API-Token': Crypto_API_TESTNET}

    data = {
        'asset': "USDT",
        'amount': float(price) * 0.8,
        'user_id': to_id,
        'spend_id': f"HGEQ{random.randint(1, 1238)}N5K"
    }

    response = post("https://testnet-pay.crypt.bot/api/transfer", headers=headers, data=data)