# variables/ — données d'environnement et localisateurs partagés

- `env_<env>.yaml` — données d'environnement (URLs de base, tenant, jeux de
  données) ; les fichiers YAML exigent PyYAML (`pip install pyyaml`), les
  fichiers `.py` n'exigent rien.
- `locators.py` (optionnel) — sélecteurs partagés entre PLUSIEURS page
  objects ; si un sélecteur ne sert qu'à une page, il reste dans son
  `resources/page_objects/<page>.resource`.

**Jamais de mot de passe ici** : les credentials passent en variables typées
`Secret:` sur la ligne de commande (Robot Framework 7.4+, masquées même au
niveau TRACE) :

```
robot -v "APP_PASSWORD: Secret:..." tests/robot/ui/web/ma_suite.robot
```
