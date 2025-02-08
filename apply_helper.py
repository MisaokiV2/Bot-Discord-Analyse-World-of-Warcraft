import discord
from discord import app_commands

import business as bsn
import re
from dotenv import load_dotenv
import os

from business import manager

# Charger les variables d'environnement
load_dotenv()
ROLE_MURLOK = 1304187182038122546
ROLE_OFFICIER =  1336252708902011002#1304186079783686165
TOKEN = os.getenv("DISCORD_TOKEN")
TICKET_TOOL_ID = 557628352828014614
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
guild = discord.Object(id=1126886444636582049)

# Gestionnaire d'événements : bot prêt
@client.event
async def on_ready():
    """tree.clear_commands(guild=None)
    await tree.sync(guild=None)"""
    await bsn.manager.setup(tree, guild=guild)  # Charger les commandes
    await tree.sync(guild=guild)  # Synchroniser les commandes sur Discord
    print(f"Connecté en tant que {client.user} et commandes slash synchronisées")

@client.event
async def on_message(message):
    """Crée un channel privé et stocke le lien dans un fichier JSON."""

    # Vérifie si le message vient d'un serveur (ignore les MP)
    if message.guild is None:
        return

    officier_role = discord.utils.get(message.guild.roles, id=ROLE_OFFICIER)

    # Vérifie si le message provient de Ticket Tool
    if message.author.id == TICKET_TOOL_ID:
        user_id_match = re.search(r"<@(\d+)>", message.content)

        if user_id_match:
            user_id = int(user_id_match.group(1))  # Récupère l'ID utilisateur mentionné
            user = message.guild.get_member(user_id)  # Cherche l'utilisateur dans le serveur

            if user:
                category = discord.utils.get(message.guild.categories, name="WELCOME")

                # Si la catégorie n'existe pas, la créer
                if category is None:
                    category = await message.guild.create_category(
                        "Tickets", overwrites={
                            message.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                            officier_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
                        }
                    )

                # Création du channel privé
                channel_name = f"{user.name}"
                overwrites = {
                    message.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    officier_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
                }
                ticket_channel = await message.guild.create_text_channel(
                    channel_name, category=category, overwrites=overwrites
                )

                # Enregistrer le lien dans le fichier JSON
                manager.add_linked_channel(message.channel.id, ticket_channel.id)

                await ticket_channel.send(f"{officier_role.mention}, un nouveau ticket a été ouvert ! 🚀")

# Lancer le bot
client.run(TOKEN)