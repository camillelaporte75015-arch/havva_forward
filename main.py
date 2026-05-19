from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChatWriteForbiddenError, RPCError
import asyncio
import random

api_id = 36710092
api_hash = "a7e65ac56a86fd316864ddc2f0668c1c"

SOURCE_CHAT = "ua_logs"
MESSAGE_ID = 3

client = TelegramClient("session", api_id, api_hash)

PAUSE_BETWEEN_ROUNDS = 300  # 5 min
MAX_CONCURRENT = 5  # ↓ réduit pour éviter FloodWait

# sécurité globale anti spam
MIN_DELAY = 1.5
MAX_DELAY = 3.5


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

            # petite pause entre chaque envoi (IMPORTANT)
            await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

        except FloodWaitError as e:
            wait_time = e.seconds + 5
            print(f"⚠️ FloodWait {wait_time}s -> {getattr(channel, 'title', 'unknown')}")
            await asyncio.sleep(wait_time)

        except ChatWriteForbiddenError:
            print(f"⛔ Impossible d'écrire -> {getattr(channel, 'title', 'unknown')}")

        except RPCError as e:
            print(f"❌ RPC Error -> {e}")

        except Exception as e:
            print(f"❌ Erreur -> {getattr(channel, 'title', 'unknown')}: {e}")


async def main():
    await client.start()
    print("✅ Userbot connecté")

    source = await client.get_entity(SOURCE_CHAT)

    while True:
        try:
            msg = await client.get_messages(source, ids=MESSAGE_ID)

            if not msg:
                print("❌ Message introuvable")
                await asyncio.sleep(30)
                continue

            channels = await get_channels()
            print(f"📢 {len(channels)} canaux trouvés")

            semaphore = asyncio.Semaphore(MAX_CONCURRENT)

            tasks = [
                send_to_channel(channel, msg, semaphore)
                for channel in channels
            ]

            await asyncio.gather(*tasks)

            print("✅ Cycle terminé")
            print("⏳ Pause 5 minutes...\n")

            await asyncio.sleep(PAUSE_BETWEEN_ROUNDS)

        except Exception as e:
            print(f"❌ Erreur globale: {e}")
            await asyncio.sleep(30)


with client:
    client.loop.run_until_complete(main())
