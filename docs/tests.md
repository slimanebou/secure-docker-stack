# Tests de validation

| Test | Commande | Résultat |
|---|---|---|
| Recréation du conteneur db | `docker compose up -d --force-recreate db` | ID modifié, client "Test Persistance" conservé |
| Arrêt complet | `docker compose down` puis `up -d` | Données conservées, init.sql non rejoué ("Skipping initialization") |
| Persistance Redis (AOF) | `SET` → recréation → `GET` | "survit" |
| DNS app → db, redis | `getent hosts db redis` | Résolus (172.20.0.x) |
| Isolation nginx → redis | `nslookup redis` | NXDOMAIN |
| Isolation redis → Internet | `ping 8.8.8.8` | Network unreachable |