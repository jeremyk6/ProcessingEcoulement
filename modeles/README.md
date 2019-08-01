# Modèles

### Supprimer les ponts - *suppression_ponts.model3*

* Entrées :
  * Constructions linéaires : Linéaire vecteur
  * Constructions surfaciques : Surfacique vecteur
  * Cours d'eau : Linéaire vecteur
  * Emprise : Emprise géographique
  * MNT : Raster
  * Résolution : Entier
* Sorties :
  * Résultat : Raster
  * Différences : Raster
  * Tampons : Surfacique vecteur
* Description : Supprimer les ponts qui intersectent avec un cours d'eau présents sur un MNT par interpolation IDW; en se basant sur des données vectorielles.

### Recaler un raster - *recalage_raster.model3*

* Entrées :
  * Raster à recaler : Raster
  * Raster source : Raster
  * Résolution : Entier
* Sorties :
  * Raster recalé : Raster
* Description : Recale un raster sur la grille d'un second raster.

### Intégration du MNT intermédiaire - *integration_mnt.model3*

* Entrées :
  * MNT à intégrer : Raster
  * MNT original : Raster
  * Seuil de différence : Réel
* Sorties :
  * MNT intégré : Raster
* Description : Intègre un MNT intermédiaire au MNT original en ne prenant en compte que les valeurs inférieure ou égales au MNT original auquel on soustrait un seuil de différence pour limiter l'impact en dehors des berges et éliminer les éventuelles nouvelles obstructions.
