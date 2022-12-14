import asyncio
import aiohttp

from web3.auto import w3
from loguru import logger
from aiohttp import ClientSession
from eth_account.messages import encode_defunct
from pyuseragents import random as random_useragent


def create_wallet():
    account = w3.eth.account.create()
    return(str(account.address), str(account.privateKey.hex()))


def create_signature(nonce: str, private_key: str):
    message = encode_defunct(text=nonce)
    signed_message = w3.eth.account.sign_message(message, private_key)
    return(signed_message.signature.hex())


async def main():
    while True:
        try:
            async with aiohttp.ClientSession() as client:

                address, private_key = create_wallet()
                user_agent = random_useragent()

                await client.get(f'https://api.crew3.xyz/communities/invitations/{ref}',
                             headers={
                                 'origin': f'https://{name}.crew3.xyz',
                                 'user-agent': user_agent
                             })

                logger.info('Sending wallet')
                response = await client.post('https://api.crew3.xyz/authentification/wallet/nonce',
                                  data={
                                      "address": address
                                  }, headers={
                                      'origin': f'https://{name}.crew3.xyz',
                                      'user-agent': user_agent
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
                                  }, headers={
                                      'origin': f'https://{name}.crew3.xyz',
                                      'user-agent': user_agent
                                  })
                access_token = (response.headers)['Set-Cookie'].split(';')[0]

                logger.info('Completing a task')
                if task_type == 1:
                    response = await client.post(f'https://api.crew3.xyz/communities/{name}/quests/{quest_id}/claim',
                                      data={
                                          "questId": quest_id,
                                          "type": 'none'
                                      }, headers={
                                          'origin': f'https://{name}.crew3.xyz',
                                          'cookie': access_token,
                                          'user-agent': user_agent
                                      })
                    (await response.json())['status']
                else:
                    response = await client.post(f'https://api.crew3.xyz/communities/{name}/quests/{quest_id}/claim',
                                      data={
                                          "value": "joined",
                                          "questId": quest_id,
                                          "type": 'telegram'
                                      }, headers={
                                          'origin': f'https://{name}.crew3.xyz',
                                          'cookie': access_token,
                                          'user-agent': user_agent
                                      })
                    (await response.json())['status']
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
    delay = int(input('Delay(sec): '))

    asyncio.run(main())
