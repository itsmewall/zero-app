.PHONY: init run fmt test mig-up mig-gen

init:        ## instala pre-commit e deps
	pip install -r requirements.txt
	pre-commit install

run:         ## roda api com reload
	FLASK_APP=app flask run --host=0.0.0.0 --port=8000

fmt:         ## formata
	black . && isort .

test:        ## testes
	pytest -q

mig-up:
	flask db upgrade

mig-gen:
	flask db migrate -m "$(m)"