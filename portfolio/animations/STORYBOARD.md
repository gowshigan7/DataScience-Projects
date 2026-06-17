# Storyboard — 10 animations DS / AI / CS

But : 10 boucles animées, **uniformes**, illustrant des concepts réels de data science /
IA / informatique — réutilisables comme vignettes de projets, fonds de section, ou
« showreel ». Chaque scène est ancrée dans le travail de Gowshigan (embeddings/RAG,
GMM, systèmes distribués…) et partage **un seul langage visuel** (ci-dessous).

---

## 1. Système visuel commun (la garantie d'uniformité)

Tout ce qui suit est **identique pour les 10 scènes**. Une scène ne choisit que *son
concept* ; jamais sa palette, son tempo ni sa typo.

| Axe | Spécification unique |
|---|---|
| **Format** | 1200 × 675 (16:9), `viewBox` responsive, rendu @2x |
| **Fond** | `#0e0d0f` + grille ténue `#1b1820` (lignes 1px, pas de 48px) |
| **Palette** | teal `#2fc3b4` = élément **actif/courant** · clay `#df7a57` = données/secondaire · sand `#e8a766` = **résultat/highlight** · dim `#6a778f` = inactif |
| **Texte** | mono **JetBrains Mono**, label en bas-gauche (ex. `// gradient descent`), 14px, `#b0a6a0` |
| **Boucle** | **6 s**, parfaitement bouclée (frame 0 = frame finale) |
| **Cadence** | 60 fps, easing global `cubic-bezier(0.22, 1, 0.36, 1)` |
| **Particules** | points r = 1.5–3 px · liens 1px, alpha 0.08–0.16 · glow doux sur l'actif |
| **Marges** | safe-area 64px ; le label et le concept ne touchent jamais le bord |
| **Accessibilité** | `prefers-reduced-motion` → frame statique représentative, aucune boucle |
| **Signature** | chaque scène culmine sur **un seul** moment fort (le « résultat » en sand) |

**Principe de mouvement (frontend-design)** : l'audace dans un seul geste par scène, le
reste calme. On montre un concept qui *converge* — l'œil suit l'état actif (teal) jusqu'au
résultat (sand). Pas d'effets dispersés.

---

## 2. Les 10 scènes

Tempo commun en 4 temps : **0s** établir · **2s** agir · **4s** converger · **6s** résoudre → reboucle.

| # | id | Concept (DS/AI/CS) | Ce qui s'anime | Résolution (sand) | Ancrage |
|---|----|--------------------|----------------|-------------------|---------|
| 01 | `latent-space` | Embeddings & RAG | nuage de vecteurs dérive en 3 clusters gaussiens ; une *query* tire ses plus proches voisins | les k voisins s'allument | RAG, Pinecone |
| 02 | `gradient-descent` | Optimisation | une bille descend des courbes de niveau d'une loss, trace son chemin | atteint le minimum global | entraînement ML |
| 03 | `neural-net` | Forward pass (MLP) | impulsions parcourent les arêtes couche par couche, poids qui s'éclairent | neurone de sortie s'active | deep learning |
| 04 | `k-means` | Clustering non supervisé | points se recolorent à chaque réassignation, centroïdes glissent | centroïdes stabilisés | ML non supervisé |
| 05 | `decision-boundary` | Classification | 2 classes de points ; une frontière se courbe pour les séparer | marge nette tracée | SVM / régression log. |
| 06 | `attention` | Transformer / LLM | rangée de tokens ; liens d'attention pondérés s'allument token→token | tête d'attention dominante | attention, RAG |
| 07 | `gmm-density` | Mixture gaussienne (EM) | 3 cloches de densité respirent et se réajustent (étapes E/M) | mélange ajusté aux points | **GMM-from-scratch** |
| 08 | `sorting` | Algorithmes | barres comparées/permutées (quicksort), pivots en teal | tableau trié dégradé | fondamentaux CS |
| 09 | `graph-search` | Graphes / distribué | front d'onde BFS/Dijkstra se propage de nœud en nœud | plus court chemin illuminé | systèmes distribués (UPEC) |
| 10 | `convolution` | CNN / tenseurs | noyau glisse sur une feature-map, cases échantillonnées | carte de sortie révélée | vision / tenseurs |

---

## 3. Détail par scène (temps clés)

> Format : `0s → 2s → 4s → 6s`. Tout reboucle proprement à 6s.

- **01 latent-space** — points épars → dérive vers 3 clusters → une query (teal vif) émet un rayon → ses k-NN passent en sand. *(réutilise la signature du hero.)*
- **02 gradient-descent** — contours + bille en haut → la bille glisse en zig-zag amorti → ralentit près du creux → se pose au minimum (pulse sand).
- **03 neural-net** — réseau 4-6-6-2 au repos → impulsions entrent (clay) → se propagent couche par couche → la sortie s'illumine (sand), puis fondu.
- **04 k-means** — points gris + 3 centroïdes → assignation (points prennent la couleur du centroïde) → centroïdes se déplacent (moyenne) → convergence, halo sand.
- **05 decision-boundary** — 2 nuages mêlés → frontière droite apparaît → se courbe pour épouser les classes → marge + zones teintées (sand sur la marge).
- **06 attention** — 8 tokens alignés → liens faibles partout → pondérations montent (épaisseur/teal) → une tête domine, token-clé en sand.
- **07 gmm-density** — points + 3 cloches floues → E-step (responsabilités colorent les points) → M-step (cloches bougent/scalent) → densité épouse les points (sand).
- **08 sorting** — barres aléatoires → pivot teal, comparaisons → permutations animées → tableau trié, dégradé teal→sand.
- **09 graph-search** — graphe de ~14 nœuds → source pulse → front d'onde teal de proche en proche → plus court chemin en sand.
- **10 convolution** — feature-map (grille) + noyau 3×3 teal → glisse case par case → chaque position calcule une sortie → carte de sortie révélée (sand).

---

## 4. Rendu : quelle techno ? (à trancher)

| Approche | Rend le mieux pour… | Poids / Qualité | Verdict |
|---|---|---|---|
| **Canvas/SVG web natif** (1 moteur, 10 scènes) | **embarquer sur le site** (vignettes, fonds) | minuscule, vectoriel net à toute taille, instantané, accessible | ✅ **recommandé** pour le portfolio |
| **Remotion → MP4/GIF** | **clips sociaux / showreel** (LinkedIn, posts) | lourd à installer, raster (non scalable), fichiers plus gros, temps de rendu | utile **en plus**, pour exporter des vidéos |

**Ma reco** : construire les 10 en **canvas web natif** (même moteur partagé = uniformité
garantie, exactement comme la signature « latent » du hero), puis — si tu veux des vidéos —
**exporter** les scènes voulues en MP4 via Remotion ou capture de frames. Le même code de
scène peut alimenter les deux.

---

## 5. Architecture prévue (à la construction)

```
animations/
  STORYBOARD.md           ← ce fichier
  engine.js               ← moteur commun : canvas, palette, grille, loop 6s, label, reduced-motion
  scenes/
    01-latent-space.js     ← une fonction draw(ctx, t) par scène, t ∈ [0,1)
    02-gradient-descent.js
    ... (10)
  gallery.html            ← grille des 10 pour tout prévisualiser d'un coup
```

Chaque scène = **une fonction pure `draw(ctx, t, palette)`**, `t` normalisé sur la boucle.
Le moteur impose le format, la palette, la grille, le label et le timing → **uniformité par
construction**.
