### ナレッジをファイルパスから作成する
https://docs.phidata.com/knowledge/pdf#pdf-knowledge-base

docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5532:5432 \
  --name pgvector \
  phidata/pgvector:16

### "psycopg[binary]"のpoetryでinstallする方法
```
poetry add "psycopg[binary]"
```


input command
```
list down all the dishes

what are the ingredients of Massaman Gai
```

### PgVector
```
docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5532:5432 \
  --name pgvector \
  phidata/pgvector:16
```
