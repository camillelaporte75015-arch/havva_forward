from telethon import TelegramClient
from telethon.errors import FloodWaitError
import asyncio
import time

api_id = 36710092
api_hash = "a7e65ac56a86fd316864ddc2f0668c1c"

SOURCE_CHAT = "ua_logs"
MESSAGE_ID = 3

client = TelegramClient("session", api_id, api_hash)

AUTO_STOP = 300  # 5 minutes
MAX_CONCURRENT = 10  # nombre d'envois simultanés


async def get_channels():
    channels = []

    async for dialog in client.iter_dialogs():
        entity = dialog.entity

        if getattr(entity, "broadcast", False) or getattr(entity, "megagroup", False):
            channels.append(entity)

    return channels


async def send_to_channel(channel, msg, semaphore):
    async with semaphore:
        try:
            await client.forward_messages(channel, msg)
            print(f"✅ Envoyé -> {getattr(channel, 'title', 'Sans nom')}")

        except FloodWaitError as e:
            print(f"⚠️ FloodWait {e.seconds}s -> {getattr(channel, 'title', 'unknown')}")
            await asyncio.sleep(e.seconds)

        except Exception as e:
            print(f"❌ Erreur {getattr(channel, 'title', 'unknown')}: {e}")


async def main():
    await client.start()
    print("Userbot connecté")

    source = await client.get_entity(SOURCE_CHAT)

    start_time = time.time()

    while True:

        # auto stop après 5 minutes
        if time.time() - start_time > AUTO_STOP:
            print("⛔ Auto-stop après 5 minutes")
            break

        try:
            msg = await client.get_messages(source, ids=MESSAGE_ID)

            if not msg:
                print("Message introuvable")
                await asyncio.sleep(10)
                continue

            channels = await get_channels()
            print(f"{len(channels)} canaux trouvés")

            semaphore = asyncio.Semaphore(MAX_CONCURRENT)

            tasks = [
                send_to_channel(channel, msg, semaphore)
                for channel in channels
            ]

            # envoi simultané
            await asyncio.gather(*tasks)

            print("✅ Tous les canaux ont reçu le message")
            print("⏳ Pause 30 secondes...\n")

            await asyncio.sleep(30)

        except Exception as e:
            print(f"Erreur globale: {e}")
            await asyncio.sleep(10)


with client:
    client.loop.run_until_complete(main())
