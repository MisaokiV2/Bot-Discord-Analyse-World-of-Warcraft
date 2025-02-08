import discord
from discord import app_commands


from api import *
from . import manager

# Commandes slash liées aux fonctionnalités générales
async def setup(tree, guild):
    print('setup lancé')

    @tree.command(name="ping", description="Answers with Pong!", guild=guild)
    async def ping(interaction):
        await interaction.response.send_message("Pong!")

    @tree.command(name="dungeon_score", description="Give mm+ score", guild=guild)
    async def dungeon_score(interaction):
        await interaction.response.send_message("Give mm+ score!")

    @tree.command(name="help", description="JEANNE AU SECOURS !", guild=guild)
    async def help_cmd(interaction):
        await interaction.response.send_message("Commands list : "
                                                "\n- /hello"
                                                "\n- /ping"
                                                "\n- /dungeon_score")

    @tree.command(name="char_analyse", description="Analyse given character", guild=guild)
    @app_commands.checks.has_permissions(administrator=True)
    async def analyse_cmd(interaction: discord.Interaction, character_name: str, realm: str):
        data_rio = raider_io.ask_api_rio_stats(character_name, realm)
        """embed = manager.analyse_character_V3(character_name, realm)
        view = View()"""
        embed, view = manager.analyse_character(character_name, realm, data_rio)

        await interaction.response.send_message(embed=embed, view=view)

    @tree.command(name="delete", description="Delete given ticket", guild=guild)
    async def delete_ticket(interaction: discord.Interaction):
        """Supprime un ticket et son channel privé s'il existe."""

        main_channel_id = interaction.channel.id

        try:
            private_channel_id = manager.get_linked_channel(main_channel_id)

            if private_channel_id:
                private_channel = interaction.guild.get_channel(private_channel_id)
                if private_channel:
                    await private_channel.delete()


                # Supprimer le lien dans le fichier JSON
                manager.delete_linked_channel(main_channel_id)

        except manager.db_access.LinkedChannelNotFoundException:
            await interaction.response.send_message("❌ Aucun channel privé lié trouvé.", ephemeral=True)
        except manager.db_access.DeleteLinkedChannelException as e:
            await interaction.response.send_message(f"⚠️ Erreur lors de la suppression du lien : {e}", ephemeral=True)
        finally:
            await interaction.channel.delete()

    @delete_ticket.error
    async def admin_command_error(interaction: discord.Interaction, error):
        """Gère les erreurs d'autorisation pour la commande delete_ticket."""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("🚫 Vous devez être administrateur pour utiliser cette commande.",
                                                    ephemeral=True)

    print('setup fini')
