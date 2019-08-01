# Scripts

### Créer des profils de validation de ponts linéaires - *profiler_ponts.py*

* Entrées :
  * Lignes de berges : Linéaire vecteur
  * Linéaire de ponts : Linéaire vecteur
  * Distance d'extension : Entier
  * Distance de décalage : Entier
* Sorties :
  * Profils de ponts : Linéaire vecteur
* Description : Permet de créer trois linéaires de validation en amont, sur le pont, et en aval dont la forme est limitée par les deux lignes de berge. La distance d'extension permet au pont contenu au sein de la berge de la toucher des deux côtés. La distance de décalage contrôle le décalage des deux profils par rapport au pont.

### Échantilloner des profils depuis des rasters - *creer_profils.py*

* Entrées :
  * Lignes : Linéaire vecteur
  * Rasters : Rasters multiples
  * Nombre d'échantillons : Entier
* Sorties :
  * Échantillons : Ponctuel vecteur
* Description : Permet d'échantilloner les valeurs d'un MNT le long d'une couche linéaire. Conserve les attributs de la ligne et ajoute un attribut elevation.

### Comparer des profils échantillonnés - *comparer_profils.py*

* Entrées :
  * Profils : Ponctuel vecteur
* Sorties :
  * Comparaison : Page HTML
* Description : Permet de comparer des profils échantillonés entre eux afin d'obtenir une moyenne des écarts ou un écart type. Sortie sous forme de rapport HTML (dépend du module yattag).

### Corriger les profils croisés - *corriger_profils.py*

* **WIP**
* Description : utilisé pour lisser l'azimuth des profils et limiter les croisements.

### Interpoler les valeurs d'une série de profils - *interpoler_valeurs_profils.py*

* Entrées :
  * Profils : Linéaire vecteur
  * MNT : Raster
  * Nombre d'échantillons : Entier
* Sorties :
  * Points : Ponctuel vecteur
* Description : Échantillonne un MNT sur une série de profils et détermine la valeur des échantillons entre le premier et le dernier profil selon une progression linéaire.

### Détecter les obstructions - *detecter_obstruction.py*

* Entrées :
  * Profils : Linéaire vecteur
  * MNT : Raster
  * Nombre d'échantillons : Entier
  * Seuil de différence : Réel
* Sorties :
  * Profils repérés : Linéaire vecteur
* Description : Détection d'obstruction à l'écoulement sur un MNT à l'aide profils tracés le long d'un linéaire. Identifie chaque obstruction par un identifiant unique sur les profils contigus concernés.
