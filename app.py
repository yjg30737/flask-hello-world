import discord
import json
from discord import app_commands

from openai import OpenAI

# Need to set the intents to default
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

openai_client = OpenAI(api_key=api_key)


# Event handler for when the bot is ready
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

# Function to implement text translation
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

# Run the bot
client.run(DISCORD_TOKEN)
