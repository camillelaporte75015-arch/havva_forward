from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChatWriteForbiddenError, RPCError
import asyncio
import random

api_id = 36710092
api_hash = "a7e65ac56a86fd316864ddc2f0668c1c"

SOURCE_CHAT = "ua_logs"
MESSAGE_ID = 3

client = TelegramClient("session_safe", api_id, api_hash)

# pauses longues pour réduire les limitations
MIN_DELAY = 90
MAX_DELAY = 180

# max de salons par cycle
MAX_CHANNELS_PER_ROUND = 8

# pause entre cycles
PAUSE_BETWEEN_ROUNDS = 1800  # 30 min


async def get_channels():
    channels = []

    async for dialog in client.iter_dialogs():
        entity = dialog.entity

        if getattr(entity, "broadcast", False) or getattr(entity, "megagroup", False):
            channels.append(entity)

    return channels


async def send_to_channel(channel, msg):
    try:
        await client.forward_messages(channel, msg)

        print(f"✅ Envoyé -> {getattr(channel, 'title', 'Sans nom')}")

    except FloodWaitError as e:
        print(f"⚠️ FloodWait {e.seconds}s")
        await asyncio.sleep(e.seconds + 15)

    except ChatWriteForbiddenError:
        print(f"⛔ Impossible d'écrire -> {getattr(channel, 'title', 'unknown')}")

    except RPCError as e:
        print(f"❌ RPC Error -> {e}")

    except Exception as e:
        print(f"❌ Erreur -> {e}")


async def main():
    await client.start()

    print("✅ Userbot connecté")

    source = await client.get_entity(SOURCE_CHAT)

    while True:
        try:
            msg = await client.get_messages(source, ids=MESSAGE_ID)

            if not msg:
                print("❌ Message introuvable")
                await asyncio.sleep(60)
                continue

            channels = await get_channels()

            # limite volontaire
            channels = channels[:MAX_CHANNELS_PER_ROUND]

            print(f"📢 {len(channels)} canaux sélectionnés")

            for channel in channels:
                await send_to_channel(channel, msg)

                delay = random.randint(MIN_DELAY, MAX_DELAY)

                print(f"⏳ Pause {delay}s")

                await asyncio.sleep(delay)

            print("✅ Cycle terminé")
            print("⏳ Pause longue avant prochain cycle\n")

            await asyncio.sleep(PAUSE_BETWEEN_ROUNDS)

        except Exception as e:
            print(f"❌ Erreur globale: {e}")
            await asyncio.sleep(60)


with client:
    client.loop.run_until_complete(main())
