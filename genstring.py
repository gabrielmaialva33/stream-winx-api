import asyncio
import os

from telethon.sessions import StringSession
from telethon.sync import TelegramClient


def install_telethon():
    try:
        from telethon import TelegramClient
    except ImportError:
        os.system("pip install telethon")
        print("\nTelethon installed successfully!")


async def generate_session(api_id, api_hash):
    print("\nStarting the String Session generation...")

    async with TelegramClient(StringSession(), api_id, api_hash) as client:
        session_string = client.session.save()

        session_message = (
            "🔴 **DO NOT SHARE YOUR STRING SESSION WITH ANYONE!** 🔴\n\n"
            f"{session_string}\n\n**STRING SESSION GENERATED SUCCESSFULLY!**"
        )

        try:
            await client.send_message("me", session_message)
            print("\n✅ String Session sent to your saved messages on Telegram!")
        except Exception as e:
            print(f"\n⚠️ Failed to send message: {e}")

        print("\n🟢 String Session generated:")
        print(session_message)
        return session_string


def start_session_generation():
    print("\n🔧 Welcome to the Telethon String Session Generator!\n")
    api_id = input("Enter your API ID:\n> ")
    api_hash = input("\nEnter your API HASH:\n> ")

    if not api_id or not api_hash:
        print("\n❌ Both API ID and API HASH are required!")
        return

    try:
        int(api_id)
    except ValueError:
        print("\n❌ API ID must be a valid number!")
        return

    asyncio.run(generate_session(api_id, api_hash))


if __name__ == "__main__":
    install_telethon()
    start_session_generation()
