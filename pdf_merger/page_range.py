"""
page_range.py
=============
Analyse des plages de pages saisies par l'utilisateur.

Description :
    Convertit une chaîne lisible (« 1-3, 5, 8- ») en liste d'indices de pages
    (base 0) pour pypdf. Les pages sont numérotées à partir de 1 côté utilisateur.

Cas d'usage :
    - Ne garder que les pages 1 à 3 d'un document
    - Garder tout à partir de la page 8 (« 8- »)
    - Inverser une plage (« 5-1 » donne 5, 4, 3, 2, 1)

Entrée  : chaîne de plage + nombre de pages du document
Sortie  : list[int] d'indices base 0, dans l'ordre demandé
"""

from pdf_merger import config


def parse_page_range(spec, page_count):
    """
    Convertit une plage de pages en indices base 0.

    Args:
        spec (str | None): plage saisie, ex. "1-3, 5, 8-". Vide, None ou
            "toutes" = toutes les pages.
        page_count (int): nombre de pages du document.

    Returns:
        list[int]: indices des pages à garder (base 0), doublons conservés.

    Raises:
        ValueError: si la plage est mal formée ou dépasse le document.
    """
    if not spec or spec.strip().lower() == config.ALL_PAGES_LABEL:
        return list(range(page_count))

    indices = []
    for part in spec.split(config.RANGE_SEPARATOR):
        part = part.strip()
        if not part:
            continue
        start, end = _parse_part(part, spec, page_count)
        step = 1 if end >= start else -1
        indices.extend(page - 1 for page in range(start, end + step, step))
    return indices


def _parse_part(part, spec, page_count):
    """
    Analyse un morceau de plage (« 4 », « 2-6 », « 8- », « -3 »).

    Args:
        part (str): morceau déjà nettoyé des espaces.
        spec (str): plage complète, pour le message d'erreur.
        page_count (int): nombre de pages du document.

    Returns:
        tuple[int, int]: (première page, dernière page), numérotées depuis 1.

    Raises:
        ValueError: si le morceau est invalide ou hors limites.
    """
    try:
        if config.RANGE_DASH in part:
            left, right = (s.strip() for s in part.split(config.RANGE_DASH, 1))
            start = int(left) if left else 1
            end = int(right) if right else page_count
        else:
            start = end = int(part)
    except ValueError:
        raise ValueError(config.ERR_BAD_RANGE.format(spec=spec)) from None

    for page in (start, end):
        if page < 1 or page > page_count:
            raise ValueError(config.ERR_RANGE_OUT.format(page=page, count=page_count))
    return start, end
