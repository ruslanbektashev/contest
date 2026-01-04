## Инструкция для развертывания в Docker:
```
git clone https://github.com/ruslanbektashev/contest.git`
cd contest
git checkout stable
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py createsuperaccount
docker compose exec -u root web python manage.py collectstatic --no-input
docker compose exec -u root web chown -R contest /app/static
docker compose exec -u root web chmod -R a+rX /app/static
```
