from telethon import TelegramClient
from telethon.errors import FloodWaitError
import asyncio

api_id = 36710092
api_hash = "a7e65ac56a86fd316864ddc2f0668c1c"

SOURCE_CHAT = "ua_logs"
MESSAGE_ID = 3

client = TelegramClient("session", api_id, api_hash)

DELAY = 3  # anti-rate par message


async def get_channels():
    channels = []

    async for dialog in client.iter_dialogs():
        entity = dialog.entity

        if getattr(entity, "broadcast", False) or getattr(entity, "megagroup", False):
            channels.append(entity)

    return channels


async def main():
    global DELAY

    await client.start()
    print("Userbot connecté")

    source = await client.get_entity(SOURCE_CHAT)

    while True:
        try:
            msg = await client.get_messages(source, ids=MESSAGE_ID)

            if not msg:
                print("Message introuvable")
                await asyncio.sleep(90)
                continue

            channels = await get_channels()
            print(f"{len(channels)} canaux trouvés")

            for channel in channels:
                try:
                    await client.forward_messages(channel, msg)
                    print(f"Envoyé -> {getattr(channel, 'title', 'Sans nom')}")

                    await asyncio.sleep(DELAY)

                except FloodWaitError as e:
                    print(f"⚠️ FloodWait détecté: {e.seconds}s")

                    # on ralentit automatiquement
                    DELAY = min(10, DELAY + 1)

                    await asyncio.sleep(e.seconds)

                except Exception as e:
                    print(f"Erreur {getattr(channel, 'title', 'unknown')}: {e}")

            print("✅ Tous les canaux ont reçu le message")
            print("⏳ Pause anti-rate 90 secondes...\n")

            # reset léger du delay si tout s'est bien passé
            DELAY = max(3, DELAY - 0.5)

            await asyncio.sleep(90)

        except Exception as e:
            print(f"Erreur globale: {e}")
            await asyncio.sleep(90)


with client:
    client.loop.run_until_complete(main())
