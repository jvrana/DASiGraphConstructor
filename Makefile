init:
	pipenv install
	pipenv run pyblast install
	yarn

run:
	export FLASK_APP=dasi
	export FLASK_ENV=developement
	pipenv run flask run

populate:
	pipenv run python cli.py --env "config.Testing" run --thread 1 - populate-database tests/testing_data/genbank_files