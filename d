from telethon.sync import TelegramClient

api_id = ""
api_hash = ""

with TelegramClient('', api_id, api_hash) as client:
    for dialog in client.iter_dialogs():
        print(dialog.name, 'has ID', dialog.id)
