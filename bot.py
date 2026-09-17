import discord
from discord.ext import commands
import os
import tempfile
import asyncio
from aiohttp import web
from config import DISCORD_TOKEN, MAX_UPLOAD_BYTES
from deobfuscator.pipeline import DeobfuscationPipeline

async def handle_ping(request):
    return web.Response(text="Deobfuscator Bot is online!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def setup_hook():
    bot.loop.create_task(start_web_server())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.command(name="deob")
async def deobfuscate(ctx):
    if not ctx.message.attachments:
        await ctx.send("❌ Please upload a `.lua` or `.luau` file with the `.deob` command.")
        return

    attachment = ctx.message.attachments[0]
    filename = attachment.filename.lower()
    
    if not (filename.endswith(".lua") or filename.endswith(".luau")):
        await ctx.send("❌ Invalid file type. Only `.lua` and `.luau` are supported.")
        return

    if attachment.size > MAX_UPLOAD_BYTES:
        await ctx.send(f"❌ File too large. Max upload size is {MAX_UPLOAD_BYTES / (1024*1024):.2f} MB.")
        return

    status_msg = await ctx.send("🔍 Analyzing Lua/Luau source...")

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "obfuscated.lua")
        output_path = os.path.join(temp_dir, "deobfuscated.lua")
        
        try:
            await attachment.save(input_path)
            
            with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()

            pipeline = DeobfuscationPipeline()
            result = await asyncio.to_thread(pipeline.run, source)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result.source)
            
            summary = "\n".join([f"✓ {stage}" for stage in result.stages])
            msg_content = f"🔍 Analysis started\n\n{summary}\n\n✅ Deobfuscation completed."

            await status_msg.edit(content=msg_content)
            await ctx.send(file=discord.File(output_path, filename="deobfuscated.lua"))

        except Exception as e:
            print(f"Error during deobfuscation: {e}")
            await status_msg.edit(content="❌ An internal error occurred while parsing the file.")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN environment variable is not set.")
    bot.run(DISCORD_TOKEN)
 
