import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from config import BOT_TOKEN, API_ID, API_HASH, GPLINKS_API, EARNLINKS_API

app = Client("chain_shortener", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# ── Step 1: Shorten with GPLinks ──────────────────────────────────────────────
async def shorten_gplinks(session: aiohttp.ClientSession, url: str) -> str:
    params = {"api": GPLINKS_API, "url": url}
    async with session.get("https://gplinks.in/api", params=params) as resp:
        data = await resp.json(content_type=None)
    if data.get("status") == "success":
        return data["shortenedUrl"]
    raise Exception(f"GPLinks error: {data.get('message', 'Unknown error')}")


# ── Step 2: Shorten with EarnLinks ───────────────────────────────────────────
async def shorten_earnlinks(session: aiohttp.ClientSession, url: str) -> str:
    params = {"api": EARNLINKS_API, "url": url}
    async with session.get("https://earnlinks.in/api", params=params) as resp:
        data = await resp.json(content_type=None)
    if data.get("status") == "success":
        return data["shortenedUrl"]
    raise Exception(f"EarnLinks error: {data.get('message', 'Unknown error')}")


# ── Main chain function ───────────────────────────────────────────────────────
async def chain_shorten(original_url: str) -> str:
    async with aiohttp.ClientSession() as session:
        step1 = await shorten_gplinks(session, original_url)   # original → gplinks
        step2 = await shorten_earnlinks(session, step1)        # gplinks  → earnlinks
    return step2


# ── Bot handler ───────────────────────────────────────────────────────────────
@app.on_message(filters.private & filters.text)
async def handle_message(client: Client, message: Message):
    text = message.text.strip()

    if not (text.startswith("http://") or text.startswith("https://")):
        await message.reply("Please send a valid URL starting with http:// or https://")
        return

    msg = await message.reply("⏳ Processing your link...")

    try:
        final_link = await chain_shorten(text)
        await msg.edit(
            f"✅ **Done!**\n\n"
            f"🔗 **Final Link:**\n`{final_link}`\n\n"
            f"**Chain:** GPLinks → EarnLinks"
        )
    except Exception as e:
        await msg.edit(f"❌ **Error:** {str(e)}")


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Bot started...")
    app.run()
