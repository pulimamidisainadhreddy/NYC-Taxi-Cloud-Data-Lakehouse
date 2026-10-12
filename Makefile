install:
	pip install -r requirements.txt
quality:
	ruff check .
	black --check .
	pytest -q
up:
	docker compose up -d --build
down:
	docker compose down
logs:
	docker compose logs -f
