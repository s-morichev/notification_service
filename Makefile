auth-init:
	docker compose exec auth flask db upgrade
	docker compose exec auth flask insert-roles
	docker compose exec auth flask createsuperuser --email superuser --password password

admin-notifications-init:
	docker compose exec admin_notifications python manage.py migrate
	docker compose exec admin_notifications python manage.py collectstatic --no-input
	docker compose exec -e DJANGO_SUPERUSER_PASSWORD=password admin_notifications python manage.py createsuperuser --username superuser --email admin@example.com --no-input


dev-run:
	docker compose up --build -d
	sleep 5  # ждем запуск постгрес для применения миграций
	$(MAKE) auth-init
	$(MAKE) admin-notifications-init


format:
	black .
	isort .

lint:
	black --check .
	isort --check-only .
	flake8 .
