import json
import boto3
from telethon import TelegramClient, events
from telethon.tl.types import InputPeerUser, InputPeerChannel, InputPeerChat, User, Channel, Chat
from telethon.tl.functions.messages import ForwardMessagesRequest

# AWS Secrets Manager
session = boto3.session.Session()
client_secret = session.client(
    service_name='secretsmanager',
    region_name='eu-north-1'  # update this with your AWS region
)
get_secret_value_response = client_secret.get_secret_value(
    SecretId='TelegramAPI'  # update this with your secret's name
)

secret = get_secret_value_response['SecretString']

# parsing the secret string to extract necessary secrets
secret_dict = json.loads(secret)
second_api_id, second_api_hash, second_app_name, first_chat_id, second_chat_id = None, None, None, None, None
if 'second_api_id' in secret_dict and 'second_api_hash' in secret_dict and 'second_app_name' in secret_dict and 'first_chat_id' in secret_dict and 'second_chat_id' in secret_dict:
    second_api_id = int(secret_dict['second_api_id'])
    second_api_hash = secret_dict['second_api_hash']
    second_app_name = secret_dict['second_app_name']
    first_chat_id = int(secret_dict['first_chat_id'])
    second_chat_id = int(secret_dict['second_chat_id'])

print("Fetched secrets from AWS Secrets Manager:")
print("Second API ID:", second_api_id)
print("Second API Hash:", second_api_hash)
print("Second App Name:", second_app_name)
print("First Chat ID:", first_chat_id)
print("Second Chat ID:", second_chat_id)

if not all([second_api_id, second_api_hash, second_app_name, first_chat_id, second_chat_id]):
    raise Exception("Couldn't retrieve all secrets from AWS Secrets Manager")

# Telegram 2 API Initialization
client = TelegramClient(second_app_name, second_api_id, second_api_hash)

@client.on(events.NewMessage(chats=(first_chat_id,)))
async def my_event_handler(event):
    print("New message received")

    second_entity = await client.get_entity(second_chat_id)
    print(f'Second entity: {type(second_entity)} - ID: {second_entity.id}')

    if isinstance(second_entity, User):
        # The second chat is a user
        to_peer = InputPeerUser(second_entity.id, second_entity.access_hash)
    elif isinstance(second_entity, Channel):
        # The second chat is a channel
        to_peer = InputPeerChannel(second_entity.id, second_entity.access_hash)
    elif isinstance(second_entity, Chat):
        # The second chat is a group
        to_peer = InputPeerChat(second_entity.id)

    # Explicitly fetch the first chat entity
    first_entity = await client.get_entity(first_chat_id)
    print(f'First entity: {type(first_entity)} - ID: {first_entity.id}')

    if isinstance(first_entity, User):
        from_peer = InputPeerUser(first_entity.id, first_entity.access_hash)
    elif isinstance(first_entity, Channel):
        from_peer = InputPeerChannel(first_entity.id, first_entity.access_hash)
    elif isinstance(first_entity, Chat):
        from_peer = InputPeerChat(first_entity.id)

    await client.send_message(to_peer, 'Test message')

    fwd_message = ForwardMessagesRequest(
        from_peer=from_peer,
        id=[event.message.id],
        to_peer=to_peer
    )

    print(f'From peer: {from_peer.to_dict()}')
    print(f'To peer: {to_peer.to_dict()}')
    print(f'Message id: {event.message.id}')
    await client(fwd_message)


with client:
    client.start()
    client.run_until_disconnected()
