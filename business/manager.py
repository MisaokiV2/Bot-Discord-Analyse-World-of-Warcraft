from . import commands as cmd
import discord
from discord.ui import View, Button, Select
from api import db_access


async def setup(tree, guild):
    await cmd.setup(tree, guild)

def analyse_character(character_name, realm, data_rio):
    view = View()
    embed = discord.Embed(title=f"Outils d'analyse pour {character_name}-{realm}", description="Voici les outils à votre disposition :", color=discord.Color.dark_embed())
    select = Select(
        placeholder="Choisissez une option d'analyse...",
        options=[
            discord.SelectOption(label="📊 Scan Complet", description="Affiche un rapport complet",
                                 value="complete_scan"),
            discord.SelectOption(label="🎯 Score RIO", description="Affiche le score Raider.IO",
                                 value="score_rio"),
            discord.SelectOption(label="📈 Progression", description="Affiche la progression du joueur",
                                 value="progression"),
            discord.SelectOption(label="⏪ Semaine précédente", description="Affiche les 8 clefs les plus hautes de la semaine précédente",
                                 value="previous_week"),
            discord.SelectOption(label="📅 Semaine actuelle", description="Affiche les 8 clefs les plus hautes de la semaine en cours",
                                 value="actual_week"),
            discord.SelectOption(label="🔑 Plus hautes clefs", description="Affiche le plus haut niveau de chacune des clefs réussie par le joueur",
                                 value="highest_key"),
        ]
    )

    async def select_callback(interaction: discord.Interaction):
        if select.values[0] == "complete_scan":
            edited_embed = discord.Embed(title=f"📊 Scan Complet                                                                 ", color=discord.Color.blue())
            edited_embed.description = "Données complètes en cours de récupération..."  # Ajouter ici les vraies données
            await interaction.response.edit_message(embed=edited_embed, view=view)
        elif select.values[0] == "score_rio":
            edited_embed = discord.Embed(title=f"🎯historique des score Raider.IO                                                               ", color=discord.Color.green())
            await interaction.response.edit_message(embed=score_io_embed(edited_embed, data_rio),view=view) #score_io_embed(edited_embed, data_rio)
        elif select.values[0] == "progression":
            edited_embed = discord.Embed(title=f"📈 Historique de progression                                                                 ", color=discord.Color.orange())
            await interaction.response.edit_message(embed=progression_embed(edited_embed, data_rio), view=view) #progression_embed(edited_embed, data_rio)
        elif select.values[0] == "previous_week":
            edited_embed = discord.Embed(title=f"⏪ Historique des clefs de la semaine précédente                                                                     ", color=discord.Color.green())
            await interaction.response.edit_message(embed=previous_week_embed(edited_embed, data_rio), view=view) #previous_week_embed(edited_embed, data_rio)
        elif select.values[0] == "actual_week":
            edited_embed = discord.Embed(title=f"📅 Récapitulatif des clefs de cette semaine                                                               ", color=discord.Color.green())
            await interaction.response.edit_message(embed=actual_week_embed(edited_embed, data_rio), view=view)  #actual_week_embed(edited_embed, data_rio)
        elif select.values[0] == "highest_key":
            edited_embed = discord.Embed(title=f"🔑 Highlight des plus hautes clefs réussies par le joueur"                                               , color=discord.Color.red())
            await interaction.response.edit_message(embed=highest_key_embed(edited_embed, data_rio), view=view) #highest_key_embed(edited_embed, data_rio)
    select.callback = select_callback

    # Ajouter le menu déroulant à la vue
    view.add_item(select)

    return embed, view

def create_button(character_name, realm, view):

    scan_button = Button(label="📊", style=discord.ButtonStyle.primary, custom_id="complete_scan")
    score_button = Button(label="🎯", style=discord.ButtonStyle.primary, custom_id="score_rio")
    progression_button = Button(label="📈", style=discord.ButtonStyle.primary, custom_id="progression")

    # Définition des callbacks pour chaque bouton
    @scan_button.callback
    async def full_scan(interaction: discord.Interaction):
        await interaction.response.send_message(f"Scan complet lancé pour {character_name} - {realm}.")

    @score_button.callback
    async def show_score(interaction: discord.Interaction):
        await interaction.response.send_message(f"Affichage du score Raider.IO pour {character_name} - {realm}.")

    @progression_button.callback
    async def show_progress(interaction: discord.Interaction):
        interaction.response.send_message(f"Affichage de la progression pour {character_name} - {realm}.")

    # Ajouter les boutons à la vue manuellement
    view.add_item(scan_button)
    view.add_item(score_button)
    view.add_item(progression_button)

    print("Vue avec boutons créée:", view)
    return view

def score_io_embed(embed, data_rio):
    embed.description = get_description(data_rio)
    # endregion

    # region season_score
    scores_by_season = data_rio.get("mythic_plus_scores_by_season", [])
    embed.add_field(name="Score Mythic+ par saison:\n", value="\u200b", inline=False)
    for season in scores_by_season:
        season_name = season['season']
        overall_score = season.get("scores", {}).get("all", "N/A")
        embed.add_field(name=f"\t{season_name}: ", value=f"{overall_score}", inline=False)
    # endregion
    return embed

def progression_embed(embed, data_rio):
    embed.description = get_description(data_rio)
    raid_achievement_curve = data_rio.get("raid_achievement_curve", [])
    for raid in raid_achievement_curve:
        raid_name = raid.get("raid", "Unknown Raid")
        aotc = "AOTC" if "aotc" in raid else "N/A"
        ce = ", Cutting Edge" if "cutting_edge" in raid else "N/A"
        embed.add_field(name=f"{raid_name}: ", value=f"{aotc}-{ce}", inline=False)

    return embed

def actual_week_embed(embed, data_rio):
    index = 0
    this_week_runs = data_rio.get("mythic_plus_weekly_highest_level_runs", [])
    embed, index = get_specific_week_run(embed, data_rio, this_week_runs, index)
    desc = get_description(data_rio)
    embed.description = f"{desc} a fait {index} clef" + f"{"s" if index > 1 else ""}" + " cette semaine"
    return embed

def previous_week_embed(embed, data_rio):
    index = 0
    last_week_runs = data_rio.get("mythic_plus_previous_weekly_highest_level_runs", [])
    embed, index = get_specific_week_run(embed, data_rio, last_week_runs, index)
    desc = get_description(data_rio)
    embed.description = f" {desc}  a fait {index} clef" + f"{"s" if index > 1 else ""}" + " la semaine passée"
    return embed

def highest_key_embed(embed, data_rio):
    index = 0
    embed.description ="Les clefs les plus hautes de " + get_description(data_rio)
    highest_runs = data_rio.get("mythic_plus_best_runs", [])
    embed, index = get_specific_week_run(embed, data_rio, highest_runs, index)
    """for run in highest_runs:
        dungeon = run.get("dungeon", "Inconnu")
        mythic_level = run.get("mythic_level", "Inconnu")
        print(f"Donjon : {dungeon}, Niveau : {mythic_level}")"""
    return embed

def get_specific_week_run(embed, data_rio, runs, index):
    for index, run in enumerate(runs[:8], start=1):
        dungeon_name = run.get("dungeon", "Unknown Dungeon")
        key_level = run.get("mythic_level", "N/A")
        embed.add_field(name=f"{dungeon_name} :", value=f"{key_level}", inline=False)
    return embed, index

def get_description(data_rio):
    guild = data_rio.get("guild")
    char_name = data_rio.get("name")
    char_realm = data_rio.get('realm')
    guild_name = f'<{guild.get("name", "Unknown Guild")}>' if guild else ''
    return f"{guild_name} {char_name}-{char_realm}"

def get_linked_channel(main_channel_id):
    return db_access.get_linked_channel(main_channel_id)

def delete_linked_channel(main_channel_id):
    db_access.delete_linked_channel(main_channel_id)

def add_linked_channel(main_channel_id, private_channel_id):
    db_access.add_linked_channel(main_channel_id, private_channel_id)