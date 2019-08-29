# Modèles

## Detections sur MNT

### Détecter les obstructions sur les tronçons hydrographiques - *detecter_obstructions_troncons.model3*

* Entrées :
  * MNT : Raster
  * Distance entre les profils : Réel
  * Largeur des profils : Réel
  * Seuil de rugosité : Réel
  * Seuil de différence : Réel
  * Tronçons hydrographiques : Linéaire vecteur
* Sorties :
  * Profils repérés : Linéaire vecteur
* Description : Détecte les obstructions à l'écoulement sur un MNT sur la couche troncon_hydrographique de la BD TOPO.

## Traitements de MNT

### Rétablir les cours d'eau souterrains sur un MNT - *retablir_ce_souterrain.model3*

* Entrées :
  * MNT : Raster
  * Distance entre les profils : Réel
  * Largeur des profils : Réel
  * Résolution du MNT : Réel
  * Seuil de différence : Réel
  * Seuil de rugosité : Réel
  * Tronçons hydrographiques : Linéaire vecteur
* Sorties :
  * MNT+ce : Raster
* Description : Chaîne de traitement intégrée de détection + rétablissement des cours d'eau souterrains.

### Ajouter les bâtiments - *ajouter_batiments.model3*

* Entrées :
  * MNT original : Raster
  * Bâtiments : Surfacique vecteur
  * Résolution du MNT : Réel
* Sorties :
  * MNT+batiments : Raster
* Description : Rastérise et ajoute les bâtiments à un MNT sans bâtiments. Pour les bâtiments de hauteur nulle, récupère la hauteur du bâtiment le plus proche.

### Supprimer les ponts - *supprimer_ponts.model3*

* Entrées :
  * Constructions linéaires : Linéaire vecteur
  * Constructions surfaciques : Surfacique vecteur
  * Cours d'eau : Linéaire vecteur
  * Emprise : Emprise géographique
  * MNT : Raster
  * Résolution : Entier
* Sorties :
  * MNT-ponts : Raster
  * Différences : Raster
  * Tampons : Surfacique vecteur
* Description : Supprimer les ponts qui intersectent avec un cours d'eau présents sur un MNT par interpolation IDW; en se basant sur des données vectorielles.

## Boîte à outils raster

### Caler un raster sur une référence - *recaler_raster.model3*

* Entrées :
  * Raster à recaler : Raster
  * Raster source : Raster
  * Résolution : Entier
* Sorties :
  * Recalé : Raster
* Description : Recale un raster sur la grille d'un second raster.

### Fusionner deux MNT - *fusion_mnt.model3*

* Entrées :
  * MNT à intégrer : Raster
  * MNT original : Raster
  * Seuil de différence : Réel
* Sorties :
  * Fusionné : Raster
* Description : Intègre un MNT intermédiaire au MNT original en ne prenant en compte que les valeurs inférieure ou égales au MNT original auquel on soustrait un seuil de différence pour limiter l'impact en dehors des berges et éliminer les éventuelles nouvelles obstructions.
