# Scripts

## Détections sur MNT

### Détecter les obstructions sur une série de profils- *detecter_obstruction.py*

* Entrées :
  * Profils : Linéaire vecteur
  * MNT : Raster
  * Nombre d'échantillons : Entier
  * Seuil de différence : Réel
* Sorties :
  * Profils repérés : Linéaire vecteur
* Description : Détection d'obstruction à l'écoulement sur un MNT à l'aide de profils tracés le long d'un linéaire. Identifie chaque obstruction par un identifiant unique sur les profils contigus concernés.

### Interpoler les valeurs d'une série de profils - *interpolation_lin_profils.py*

* Entrées :
  * Profils : Linéaire vecteur
  * MNT : Raster
  * Nombre d'échantillons : Entier
* Sorties :
  * Nuage de points : Ponctuel vecteur
* Description : Échantillonne un MNT sur une série de profils et détermine la valeur des échantillons entre le premier et le dernier profil selon une progression linéaire.

## Traitements de MNT

### Intégrer un cours d'eau souterrain - *integrer_ce_sout.py*

* Entrées :
  * MNT : Raster
  * Profils repérés : Linéaire vecteur
  * Résolution : Réel
* Sorties :
  * MNT intégré : Raster
* Description : Permet d'interpoler puis intégrer au MNT des profils catégorisés comme obstrués par le traitement de détection des obstructions.

## Boîtes à outils validation

### Créer des profils de validation de ponts linéaires - *profiler_ponts.py*

* Entrées :
  * Lignes de berges : Linéaire vecteur
  * Linéaire de ponts : Linéaire vecteur
  * Distance d'extension : Entier
  * Distance de décalage : Entier
* Sorties :
  * Profils de validation : Linéaire vecteur
* Description : Permet de créer trois linéaires de validation en amont, sur le pont, et en aval dont la forme est limitée par les deux lignes de berge. La distance d'extension permet au pont contenu au sein de la berge de la toucher des deux côtés. La distance de décalage contrôle le décalage des deux profils par rapport au pont.

### Discrétiser les profils de validation - *creer_profils.py*

* Entrées :
  * Profils de validation : Linéaire vecteur
  * Rasters : Rasters multiples
  * Nombre d'échantillons : Entier
* Sorties :
  * Échantillons : Ponctuel vecteur
* Description : Permet de discrétiser les valeurs d'un MNT le long d'une couche linéaire. Conserve les attributs de la ligne et ajoute un attribut elevation.

### Comparer les profils de validation discrétisés - *comparer_profils.py*

* Entrées :
  * Profils discrétisés : Ponctuel vecteur
* Sorties :
  * Comparaison : Page HTML
* Description : Permet de comparer des profils échantillonés entre eux afin d'obtenir une moyenne des écarts ou un écart type. Sortie sous forme de rapport HTML (dépend du module yattag).