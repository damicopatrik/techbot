from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID   = 31137651
API_HASH = "1831850405c78603de836ca168c6bfc7"

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("SESSION STRING:")
    print(client.session.save())
