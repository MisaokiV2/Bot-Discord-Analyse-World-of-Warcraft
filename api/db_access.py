import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement (si besoin plus tard)
load_dotenv()

DATA_FILE = "bot_data.json"


def load_data():
    """Charge les données depuis le fichier JSON."""
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}  # Si fichier corrompu, on retourne un dictionnaire vide


def save_data(data):
    """Sauvegarde les données dans le fichier JSON."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_linked_channel(main_channel_id, private_channel_id):
    """Ajoute un lien entre un channel public et un channel privé."""
    data = load_data()

    if str(main_channel_id) in data:
        raise AddLinkedChannelException(f"Le channel {main_channel_id} est déjà lié.")

    data[str(main_channel_id)] = private_channel_id
    save_data(data)


def delete_linked_channel(main_channel_id):
    """Supprime un lien de channel s'il existe."""
    data = load_data()

    if str(main_channel_id) not in data:
        raise DeleteLinkedChannelException(f"Aucun lien trouvé pour {main_channel_id}")

    del data[str(main_channel_id)]
    save_data(data)


def get_linked_channel(main_channel_id):
    """Récupère l'ID du channel privé lié à un channel public."""
    data = load_data()

    if str(main_channel_id) not in data:
        raise LinkedChannelNotFoundException(f"Le channel {main_channel_id} n'existe pas.")

    return data[str(main_channel_id)]


# Exceptions personnalisées
class LinkedChannelNotFoundException(Exception):
    pass


class AddLinkedChannelException(Exception):
    pass


class DeleteLinkedChannelException(Exception):
    pass
