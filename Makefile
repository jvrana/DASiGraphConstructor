init:
	pipenv install
	pipenv run pyblast install
	yarn

run:
	pipenv run python cli.py --env "config.Testing" - run

populate:
	pipenv run python cli.py --env "config.Testing" - populate-database tests/testing_data/genbank_files --host "0.0.0.0" --port "5000"


inuse:
	lsof -i tcp:3000