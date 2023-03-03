import time
import requests

from web3.auto import w3
from loguru import logger
from eth_account.messages import encode_defunct
from pyuseragents import random as random_useragent


def create_wallet():
    account = w3.eth.account.create()
    return(str(account.address), str(account.privateKey.hex()))


def create_signature(nonce: str, private_key: str):
    message = encode_defunct(text=nonce)
    signed_message = w3.eth.account.sign_message(message, private_key)
    return(signed_message.signature.hex())


def main():
    for _ in range(count):
        try:
            with requests.Session() as client:
                client.headers.update({
                    'origin': 'https://crew3.xyz',
                    'user-agent': random_useragent()})

                address, private_key = create_wallet()

                client.get(
                    f'https://api.crew3.xyz/communities/invitations/{ref}')
                logger.info('Sending wallet')
                response = client.post('https://api.crew3.xyz/authentification/wallet/nonce',
                                       json={
                                           "address": address
                                       })
                data = response.json()
                session_id = data['id']
                nonce = data['nonce']

                logger.info('Verify signature')
                signature = create_signature(nonce, private_key)
                response = client.post(f'https://api.crew3.xyz/authentification/wallet/verify-signature?invitationId={ref}',
                                       json={
                                           "sessionId": session_id,
                                           "signature": signature,
                                           "network": 1
                                       })
                access_token = (response.headers)['Set-Cookie'].split(';')[0]

                client.headers.update({'cookie': access_token})

                client.patch('https://api.crew3.xyz/users/me',
                             json={
                                 "username": f'{address[:4]}...{address[-4:]}'
                             })

                logger.info('Completing a task')
                if task_type == 1:
                    client.post(f'https://api.crew3.xyz/communities/{name}/quests/{quest_id}/claim',
                                data={
                                    "questId": quest_id,
                                    "type": 'none'
                                })
                else:
                    client.post(f'https://api.crew3.xyz/communities/{name}/quests/{quest_id}/claim',
                                data={
                                    "value": "joined",
                                    "questId": quest_id,
                                    "type": 'telegram'
                                })
        except:
            logger.exception('Error\n')
        else:
            with open(f'{name}_registered.txt', 'a', encoding='utf-8') as f:
                f.write(f'{address}:{private_key}\n')
            logger.success('Successfully\n')

        time.sleep(delay)


if __name__ == '__main__':
    print("Bot Crew3 @flamingoat\n")

    task_type = input('Task type: daily claim(1) or telegram(2): ')
    name = input('Name crew3: ')
    quest_id = input('Quest id: ')
    ref = input('Ref code: ')
    count = int(input('Count: '))
    delay = int(input('Delay(sec): '))

    main()