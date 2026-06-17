# Décisions de conception — Portfolio

Ce document trace **toutes les décisions** prises pour ce portfolio et le *pourquoi*,
afin qu'on puisse itérer en connaissance de cause. Mis à jour à chaque changement structurant.

## 1. Stack technique

| Décision | Choix | Pourquoi |
|---|---|---|
| Langage | **HTML/CSS/JS vanilla** | Pas d'étape de build, démarrage instantané, facile à éditer/itérer. Un framework (React/Next) serait surdimensionné pour une page unique. |
| Build | **Aucun** | On ouvre `index.html` directement. Zéro toolchain à maintenir. |
| Polices | Google Fonts (Inter + JetBrains Mono) avec **fallback système** | Look moderne, mais le CSS retombe sur `system-ui`/monospace si le CDN est bloqué (cas du conteneur). |
| Tests | **Playwright** | Demandé explicitement. Sert au smoke-test + vérif visuelle (screenshots) pour itérer. |
| Serveur local | `http-server` (npm) ou `python3 -m http.server` | Statique, aucune dépendance lourde. |

## 2. Architecture des fichiers

```
portfolio/
├── index.html              ← markup, toutes les sections
├── styles/main.css         ← thème + layout, variables CSS en :root
├── scripts/main.js         ← nav, menu mobile, scroll-reveal (0 dépendance)
├── assets/                 ← placeholders SVG + CV PDF
├── tests/portfolio.spec.js ← tests Playwright (desktop + mobile)
├── scripts/screenshot.mjs  ← capture multi-écrans
├── playwright.config.js
├── package.json
├── README.md               ← prise en main + checklist de personnalisation
└── DECISIONS.md            ← ce fichier
```

**Principe : un fichier = une responsabilité.** Le contenu (HTML), le style (CSS) et le
comportement (JS) sont séparés pour qu'on puisse modifier l'un sans casser l'autre.

## 3. Décisions de design

- **Thème sombre** par défaut (`#0a0e1a`) : standard des portfolios tech modernes, met en valeur les accents.
- **Dégradé d'accent** cyan → violet → rose, centralisé dans la variable `--grad`. Changer 3 variables = re-skin complet.
- **Animations** : reveal au scroll via `IntersectionObserver` (perf), glow d'arrière-plan animé, micro-interactions au survol. Toutes désactivées si `prefers-reduced-motion` (accessibilité).
- **Numérotation des sections** (`01.`, `02.`…) en police mono : clin d'œil aux portfolios devs connus (style Brittany Chiang).
- **Responsive** : grilles qui passent en colonne unique < 860px, menu burger mobile.
- **Accessibilité** : skip-link, `aria-label`, contrastes, focus visible, navigation au clavier.

## 4. Stratégie « placeholders »

Demandé : mettre des placeholders pour les assets manquants.

- **Images** : SVG générés (portrait, 3 projets, image OG, favicon) — légers, nets à toute résolution, versionnables dans git (pas de binaire lourd).
- **CV** : `resume.pdf` minimal valide, à remplacer.
- **Textes** : repères explicites `[Your ...]` et `(Placeholder ...)` faciles à rechercher.
- **Profil supposé** : **Data Scientist / ML Engineer**, déduit du contenu du repo (`DataScience-Projects`). 100% modifiable.
- **Identité** : prénom « Gowshigan » et email `gowshigan6@gmail.com` repris du contexte du repo, pour un rendu réaliste tout en restant éditable.

## 5. Décisions de test

- **2 projets Playwright** : `desktop-chromium` + `mobile-chromium`.
  - *Décision* : le mobile tourne sur **Chromium** (viewport Pixel 7) et **non WebKit**, car WebKit ne démarre pas dans le conteneur (librairies système manquantes, pas de `sudo`).
- **5 tests** : titre/hero, présence des sections, chargement des images (avec scroll pour déclencher le lazy-load), navigation par ancre, absence d'erreurs console.
- **Erreurs réseau tierces ignorées** : le test « no console errors » filtre les échecs de ressources externes (Google Fonts bloquées → `ERR_CERT_AUTHORITY_INVALID`), car ce n'est pas un bug du site.
- **Screenshots** non versionnés (`.gitignore`) : régénérables via `npm run shots`, évite ~8 Mo de PNG dans git.

## 6. Contraintes d'environnement rencontrées

- **Réseau du conteneur** : HTTPS externe intercepté → Google Fonts inaccessibles. Géré par le fallback CSS + le filtre de test.
- **WebKit indisponible** : libs système manquantes → mobile testé sous Chromium.
- **Hook de formatage du repo** : `python3 .claude/hooks/post_tool_use_format.py` échoue avec un chemin relatif quand le cwd est `portfolio/`. C'est de la config du repo, sans impact sur les fichiers produits.

## 7. À décider plus tard (en attente de ton background)

- Vrais nom / titre / bio / ville.
- Vrais projets (titres, descriptions, liens, vraies captures).
- Vrai parcours (postes + dates) et liens sociaux.
- Optionnels : thème clair + toggle, section blog/certifs, formulaire de contact, déploiement (GitHub Pages / Netlify / Vercel).
