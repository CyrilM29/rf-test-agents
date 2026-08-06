# resources/page_objects/ : un `.resource` par page/écran/domaine API

Le patron *page object* en saveur Robot Framework : chaque fichier regroupe

1. en tête, les **variables de localisateurs** de LA page (ids stables,
   `data-testid`, rôle ARIA + nom accessible, jamais d'id généré) ;
2. en dessous, les **keywords métier** de cette page qui les utilisent.

Exemples de noms : `login_page.resource`, `orders_list.resource`,
`orders_api.resource`.

Créés par **rf-generator** (chaque localisateur sondé live avant écriture),
réparés par **rf-healer** (une dérive de localisateur = une ligne modifiée ici,
jamais dans un test). Les keywords partagés entre plusieurs pages vont dans
`resources/common.resource`.
