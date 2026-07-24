# Déployer GeoFacts sur Vercel

Application web **live** au-dessus du package `geolocation_facts` : un frontend
statique (`index.html`) appelle une fonction serverless Python (`api/facts.py`)
qui interroge Wikipedia en direct. Aucune dépendance externe, aucune clé API.

## Fichiers ajoutés

```
index.html            ← frontend (radar + cartes), appelle /api/facts
api/facts.py          ← fonction serverless : geolocation_facts en HTTP JSON
vercel.json           ← inclut geolocation_facts/ dans le bundle de la fonction
requirements.txt      ← (vide) déclenche le runtime Python de Vercel
```

## Déploiement — option A : depuis le dépôt GitHub (recommandé)

1. Va sur https://vercel.com → **Add New… → Project**.
2. Importe le dépôt `gowshigan7/DataScience-Projects`.
3. Laisse **Root Directory** = `./` (racine du dépôt) — `vercel.json` s'occupe du reste.
4. Framework Preset : **Other** (aucun build nécessaire).
5. **Deploy**. C'est tout : `index.html` est servi à la racine, `/api/facts` devient l'endpoint.

> La branche `claude/geolocation-fun-facts-app-06ozs1` peut être déployée telle
> quelle en « Preview ». Fusionne-la dans la branche par défaut pour la mettre en
> production.

## Déploiement — option B : CLI Vercel

```bash
npm i -g vercel
cd DataScience-Projects
vercel          # premier déploiement (preview)
vercel --prod   # mise en production
```

## L'API

`GET /api/facts` — paramètres :

| param      | ex.               | défaut | description                                  |
|------------|-------------------|--------|----------------------------------------------|
| `location` | `Berlin`          | —      | adresse (geocodée via Nominatim)             |
| `lat`,`lng`| `48.86`,`2.29`    | —      | coordonnées directes (prioritaires)          |
| `radius`   | `2`               | `3`    | rayon en km (max 10)                          |
| `limit`    | `8`               | `8`    | nombre de faits (max 30)                       |
| `lang`     | `fr`              | `en`   | langue Wikipedia                              |
| `keyword`  | `museum`          | —      | filtre par mot-clé (titre + texte)            |

Exemple :

```bash
curl "https://<ton-projet>.vercel.app/api/facts?location=Kyoto&radius=2&limit=5&lang=en"
```

Réponse :

```json
{
  "center": { "lat": 35.01, "lng": 135.76, "label": "Kyoto" },
  "count": 5, "total": 14, "radius_km": 2.0, "language": "en",
  "facts": [ { "title": "...", "fact": "...", "lat": ..., "lng": ..., "dist": 120, "url": "https://en.wikipedia.org/?curid=..." } ]
}
```

## Notes

- **Réseau sortant** : les fonctions Vercel ont accès à Internet ; l'API appelle
  Wikipedia (`geosearch` + `extracts`) et éventuellement Nominatim (geocoding).
- **Cache CDN** : les réponses sont mises en cache 1 h (`s-maxage=3600`) — mêmes
  coordonnées, mêmes faits, sans re-solliciter Wikipedia.
- **Rate limiting** : Wikipedia peut renvoyer un 429 en cas de rafale ; l'API
  répond alors proprement `502` avec un message, et le frontend l'affiche.
- **Localement** : `python -m http.server` ne sert que le statique. Pour tester
  l'API en local, utilise `vercel dev`.
