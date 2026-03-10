"""
Chargeur de plugins d'exercices.

Scanne le dossier `exercices/` à la recherche de tout module Python
contenant au moins une sous-classe concrète de `Exercice`.
"""

import importlib
import importlib.util
import pkgutil
from pathlib import Path
from typing import Type

from exercices.base import Exercice


def charger_exercices(dossier: str | Path | None = None) -> dict[str, Type[Exercice]]:
    """
    Parcourt le dossier de plugins et retourne un dict
        { NOM_exercice: ClasseExercice }

    Si `dossier` n'est pas précisé, on prend le dossier `exercices/`
    situé à côté de ce fichier.
    """
    if dossier is None:
        dossier = Path(__file__).parent

    dossier = Path(dossier)
    catalogue: dict[str, Type[Exercice]] = {}

    for finder, nom_module, _ in pkgutil.iter_modules([str(dossier)]):

        # Ignorer le module de base lui-même
        if nom_module in ("base", "__init__"):
            continue

        spec = importlib.util.spec_from_file_location(
            f"exercices.{nom_module}",
            dossier / f"{nom_module}.py",
        )
        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"[plugins] Erreur lors du chargement de '{nom_module}': {e}")
            continue

        # Collecter toutes les sous-classes concrètes de Exercice
        for attr_name in dir(module):
            cls = getattr(module, attr_name)
            if (
                isinstance(cls, type)
                and issubclass(cls, Exercice)
                and cls is not Exercice
                and cls.NOM  # ignorer les classes sans NOM défini
            ):
                catalogue[cls.NOM] = cls

    return catalogue
