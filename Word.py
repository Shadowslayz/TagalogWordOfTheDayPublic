import discord
from discord import FFmpegPCMAudio
import pyttsx3
import asyncio
from datetime import datetime, timedelta
import json
import random
import os
import sys
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# Your bot token (NEVER HARDCODE YOUR TOKEN!)
TOKEN = ''  # Store token in an environment variable

# ID of the channel where the message will be sent
CHANNEL_ID = 0  # Change these
SERVER_ID = 0

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # This is key for voice channel events
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
GUILD_ID = discord.Object(id=SERVER_ID)

JSON_FILE = "tagalog_words.json"
USED_WORDS_FILE = "used_words.json"

def load_words():
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def load_used_words():
    try:
        with open(USED_WORDS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_used_words(used_words):
    with open(USED_WORDS_FILE, "w", encoding="utf-8") as file:
        json.dump(used_words, file, indent=4)

def get_random_word():
    words = load_words()
    used_words = load_used_words()
    available_words = [word for word in words if word['word'] not in used_words]
    if not available_words:
        save_used_words([])
        available_words = words
    if available_words:
        selected_word = random.choice(available_words)
        used_words.append(selected_word['word'])
        save_used_words(used_words)
        return selected_word
    return None

def display_word(word_data):
    if not word_data:
        return "❌ No words available."
    word_text = f"\n🔹 **Tagalog Word** 🔹\n"
    word_text += f"📌 **Word:** {word_data['word']}\n"
    word_text += f"📢 **Pronunciation:** {word_data['pronunciation']}\n"
    word_text += f"📝 **Meaning:** {word_data['meaning']}\n\n"
    word_text += "**📖 Example Sentences:**\n"
    for i, example in enumerate(word_data.get("examples", []), 1):
        word_text += f"{i}. *{example['tagalog']}* - {example['english']}\n"
    return word_text

async def wait_until_midnight():
    """Waits until 12 AM and then sends a message."""
    while True:
        now = datetime.now()
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        wait_seconds = (next_midnight - now).total_seconds()
        print(f"⏳ Waiting {wait_seconds} seconds until midnight...")
        await asyncio.sleep(wait_seconds)

        # Send word of the day message
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            try:
                word_of_the_day = get_random_word()
                await channel.send(display_word(word_of_the_day))
                print(f"✅ Sent Word of the Day to channel {CHANNEL_ID}")
            except Exception as e:
                print(f"❌ Error sending message: {e}")
        else:
            print("⚠️ Error: Channel not found. Check the CHANNEL_ID.")

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    try:
        await tree.sync(guild=GUILD_ID)
        print("✅ Slash commands synced successfully.")
    except Exception as e:
        print(f"❌ Error syncing slash commands: {e}")
    client.loop.create_task(wait_until_midnight())

@tree.command(name="nextword", description="Shows the time left until the next word of the day", guild=GUILD_ID)
async def next_word(interaction: discord.Interaction):
    now = datetime.now()
    next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    remaining_time = next_midnight - now
    hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    await interaction.response.send_message(f"⏳ The next word will be sent in {hours} hours, {minutes} minutes, and {seconds} seconds.")

@tree.command(name="randomword", description="Get a random word from the dictionary", guild=GUILD_ID)
async def random_word(interaction: discord.Interaction):
    word = get_random_word()
    await interaction.response.send_message(display_word(word))

@tree.command(name="define", description="Get the definition of a specific word", guild=GUILD_ID)
async def define(interaction: discord.Interaction, word: str):
    words = load_words()
    found = next((w for w in words if w['word'].lower() == word.lower()), None)
    await interaction.response.send_message(display_word(found) if found else f"❌ The word '{word}' was not found in the dictionary.")

@tree.command(name="resetwords", description="Reset the used words list", guild=GUILD_ID)
async def reset_words(interaction: discord.Interaction):
    save_used_words([])
    await interaction.response.send_message("🔄 The used words list has been reset.")
def days_to_months_days(days):
    today = date.today()
    future_date = today + timedelta(days=days)
    
    r = relativedelta(future_date, today)
    
    return r.months, r.days

@tree.command(name="stats", description="Show statistics about word usage", guild=GUILD_ID)
async def stats(interaction: discord.Interaction):
    total_words = len(load_words())
    used_words = len(load_used_words())
    remaining_words = total_words - used_words
    months, remaining_days = days_to_months_days(remaining_words)
    await interaction.response.send_message(
        f"📊 **Word Stats:**\n✔️ Used: {used_words}\n📌 Remaining: {remaining_words}\n📚 Total: {total_words}\n⏳{months} month(s) and {remaining_days} day(s) remaining.")

@tree.command(name="pronounce", description="Get pronunciation of a word", guild=GUILD_ID)
async def pronounce(interaction: discord.Interaction, word: str):
    words = load_words()
    found = next((w for w in words if w['word'].lower() == word.lower()), None)
    await interaction.response.send_message(f"📢 **Pronunciation of {word}:** {found['pronunciation']}" if found else f"❌ Word '{word}' not found.")

@tree.command(name="example", description="Get example sentences for a word", guild=GUILD_ID)
async def example(interaction: discord.Interaction, word: str):
    words = load_words()
    found = next((w for w in words if w['word'].lower() == word.lower()), None)
    if found:
        examples = '\n'.join([f"{i+1}. *{ex['tagalog']}* - {ex['english']}" for i, ex in enumerate(found.get("examples", [])[:3])])
        await interaction.response.send_message(f"📖 **Example Sentences for {word}:**\n{examples}")
    else:
        await interaction.response.send_message(f"❌ Word '{word}' not found.")

@tree.command(name="addword", description="Add a new word to the dictionary (Admin only)", guild=GUILD_ID)
async def add_word(interaction: discord.Interaction, word: str, pronunciation: str, meaning: str, example_tl: str, example_en: str):
    words = load_words()
    if any(w['word'].lower() == word.lower() for w in words):
        await interaction.response.send_message("⚠️ This word already exists in the dictionary.")
        return
    words.append({
        "word": word,
        "pronunciation": pronunciation,
        "meaning": meaning,
        "examples": [{"tagalog": example_tl, "english": example_en}]
    })
    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(words, file, indent=4)
    await interaction.response.send_message(f"✅ The word '{word}' has been added to the dictionary.")


@tree.command(name="say", description="Reads a message aloud with voice modulation", guild=GUILD_ID)
async def say(interaction: discord.Interaction, message: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ You must be in a voice channel to use this command.")
        return
    print(f"🗣️ User {interaction.user} requested to say: {message}")
    # Disconnect if already connected
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()

    # Generate TTS audio
    tts = pyttsx3.init()
    tts.setProperty('rate', 100)  # Adjust speed as needed
    tts.setProperty('volume', 1.0)
    tts.setProperty('voice', tts.getProperty('voices')[0].id)  # Replace 0 with the index of the deep voice
    tts.save_to_file(message, "tts_output.mp3")
    tts.runAndWait()

    # Apply voice modulation using FFmpeg (e.g., pitch shift)
    os.system('ffmpeg -y -i tts_output.mp3 -af "asetrate=44100*0.6,atempo=1.5" modulated_output.mp3')
    print("✅ TTS audio generated and modulated")
    try:
        vc = await interaction.user.voice.channel.connect()
        while not vc.is_connected():
            print("⏳ Connecting to voice channel...")
            await asyncio.sleep(0.1)
        print("✅ Connected to voice channel")
        await interaction.guild.me.edit(voice_channel=vc.channel, deaf=True)
        print("✅ Bot is deafened")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to connect to voice channel: {e}")
        return
    # Play the modulated audio
    vc.play(FFmpegPCMAudio("modulated_output.mp3"))
    await interaction.response.send_message(f"🗣️ Speaking: *{message}*")

    while vc.is_playing():
        await asyncio.sleep(1)
    await vc.disconnect()

    # Clean up
    os.remove("tts_output.mp3")
    os.remove("modulated_output.mp3")


client.run(TOKEN)
