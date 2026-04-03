from telethon.sync import TelegramClient
from telethon.sessions import StringSession

SESSION_STRING = "1BJWap1sBuxxBlgCdHYYngqVHtkPCQ7Bcc3ML-2IsYhdp0RnFbI8L4R8GtUmgCCjOaNriFHzCiM3NGvkVL-JBBd3IVKWzw9DpqpUhy6DNUDbOWzHbbsmGv2t8JGLOdiODMDVbnRbKLsD7PK0n5sF7gxffLXskC3cGonQJTcRZnpZXdT4EO0JuAzlFi3_V2Kcsk-pxIJ9cV1IIITXIOQIW86uJ6BgJkun4HmvpLM0brq7Qdxuf2oqtEkFWjsfwuS8hLfEajAIVw5h4rci8NoleK7LUdnaNPPUKmTjnHedZ5nl9U0Eq9DD3PMFmiGePHG1SYWhbKPHq0KuuWfJmof1U4pExwRgSj3Y="

channels = [
    "Offerte_Tech_IPhone_Pc_Cellulari",
    "ScontiTech",
    "offertepuntotech",
    "offertesmartworld",
    "TempoDiScontiUsato",
    "offerteitalia",
]

client = TelegramClient(StringSession(SESSION_STRING), 31137651, "1831850405c78603de836ca168c6bfc7")

with client:
    for username in channels:
        try:
            entity = client.get_entity(username)
            print(f"{username} -> {entity.id}")
        except Exception as e:
            print(f"{username} -> ERRORE: {e}")
