# Scripts processing pour QGIS réalisés lors d'un stage à l'IGN

* profiler_ponts.py : utilisé pour créer trois profils entre deux berges au niveau d'un pont (en amont, sur, et en
aval).
* creer_profils.py : utilisé pour profiler une couche de lignes à partir d'un MNT. Conserve les attributs de la ligne et ajoute un attribut elevation.
* comparer_profils.py : utilisé pour comparer des profils entre eux afin d'obtenir une moyenne des écarts ou un écart type. Sortie sous forme de rapport HTML (dépend du module yattag).
* corriger_profils.py : utilisé pour lisser l'azimuth des profils et limiter les croisements.
* interpoler_valeurs_profils.py : permet l'interpolation de valeurs d'une série de profils entre le premier et le dernier.
* detecter_obstruction.py : permet la détection d'obstruction d'écoulement sur un MNT à l'aide profils tracés le long d'un linéaire.
* creer_points_raster.py : permet de créer les points à interpoler sur les profils de cours d'eau souterrains.
