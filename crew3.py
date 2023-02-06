import asyncio
import aiohttp

from web3.auto import w3
from loguru import logger
from aiohttp import ClientSession
from random import choice, randint
from aiohttp_proxy import ProxyConnector
from eth_account.messages import encode_defunct
from pyuseragents import random as random_useragent


def random_tor_proxy():
    proxy_auth = str(randint(1, 0x7fffffff)) + ':' + \
        str(randint(1, 0x7fffffff))
    proxies = f'socks5://{proxy_auth}@localhost:' + str(9150)
    return(proxies)


def get_connector():
    connector = ProxyConnector.from_url(random_tor_proxy())
    return(connector)


def create_wallet():
    account = w3.eth.account.create()
    return(str(account.address), str(account.privateKey.hex()))


def create_signature(nonce: str, private_key: str):
    message = encode_defunct(text=nonce)
    signed_message = w3.eth.account.sign_message(message, private_key)
    return(signed_message.signature.hex())


async def main():
    for i in range(count):
        try:
            async with aiohttp.ClientSession(
                connector=get_connector(),
                headers={
                    'origin': f'https://{name}.crew3.xyz',
                    'user-agent': random_useragent()}
            ) as client:

                address, private_key = create_wallet()

                await client.get(f'https://api.crew3.xyz/communities/invitations/{ref}')

                logger.info('Sending wallet')
                response = await client.post('https://api.crew3.xyz/authentification/wallet/nonce',
                                             data={
                                                 "address": address
                                             })
                data = await response.json()
                session_id = data['id']
                nonce = data['nonce']

                logger.info('Verify signature')
                signature = create_signature(nonce, private_key)
                response = await client.post(f'https://api.crew3.xyz/authentification/wallet/verify-signature?invitationId={ref}',
                                             data={
                                                 "sessionId": session_id,
                                                 "signature": signature
                                             })
                access_token = (response.headers)['Set-Cookie'].split(';')[0]

                client.headers.update({'cookie': access_token})

                await client.patch('https://api.crew3.xyz/users/me',
                                   json={
                                       "username": f'{address[:4]}...{address[-4:]}'
                                   })

                logger.info('Completing a task')
                if task_type == 1:
                    await client.post(f'https://api.crew3.xyz/communities/{name}/quests/{quest_id}/claim',
                                      data={
                                          "questId": quest_id,
                                          "type": 'none'
                                      })
                else:
                    await client.post(f'https://api.crew3.xyz/communities/{name}/quests/{quest_id}/claim',
                                      data={
                                          "value": "joined",
                                          "questId": quest_id,
                                          "type": 'telegram'
                                      })
        except:
            logger.error('Error\n')
        else:
            logger.info('Saving data')
            with open(f'{name}_registered.txt', 'a', encoding='utf-8') as f:
                f.write(f'{address}:{private_key}\n')
            logger.success('Successfully\n')

        await asyncio.sleep(delay)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    print("Bot Crew3 @flamingoat\n")

    task_type = input('Task type: daily claim(1) or telegram(2): ')
    name = input('Name crew3: ')
    quest_id = input('Quest id: ')
    ref = input('Ref code: ')
    count = int(input('Count: '))
    delay = int(input('Delay(sec): '))

    asyncio.run(main())