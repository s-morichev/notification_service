dev-run:
	docker compose up --build -d

auth-init:
	docker compose -f docker-compose.prod.yaml exec auth sh -c\
 	"flask db upgrade && flask insert-roles && flask createsuperuser --email superuser --password password"
