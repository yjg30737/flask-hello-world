import json
import os
from threading import Thread

import discord
import dotenv
from discord import app_commands
from flask import Flask
from openai import OpenAI

# Set up Flask app
app = Flask(__name__)

# Load environment variables
dotenv.load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Set the intents for the Discord bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

openai_client = OpenAI(api_key=api_key)

# Flask route
@app.route('/')
def home():
    return "Flask server is running!"

# Discord event handler for when the bot is ready
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    # Sync the slash commands
    try:
        await tree.sync()
        print("Slash commands have been synced!")
    except Exception as e:
        print(f"Error syncing slash commands: {e}")

# Register a slash command
@tree.command(name="translate", description="Translate text to a specified language")
async def translate(interaction: discord.Interaction, text: str, target_language: str = "en"):
    translated_text = await translate_text(text, target_language)
    await interaction.response.send_message(translated_text)

# Function to implement text translation using OpenAI
async def translate_text(text, target_language="en"):
    # Request translation from OpenAI
    prompt = f"Translate the following text to {target_language}: {text} and put translated text in following json format."
    prompt += """
    {
        "content": text,
    }
    """
    try:
        response = openai_client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt,
            }],
            model="gpt-4o-mini",
            response_format={"type": 'json_object'},
        )
        translated_text = response.choices[0].message.content
        return json.loads(translated_text)['content']
    except Exception as e:
        return f"Error: {str(e)}"

# Function to run Discord bot
def run_discord_bot():
    client.run(DISCORD_TOKEN)


# Start both Flask and Discord bot in separate threads
if __name__ == "__main__":
    # Run Discord bot in the main thread
    run_discord_bot()
