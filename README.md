# DASi

## Technology Stack

1. Flask
1. SQLAlchemy + extensions
1. GraphQL / graphene

## Installation

`make`

## Testing



## Requirements

1. parser-service
1. pyblast

## Usage

List environments
```
python run.py run envs
```

Run an environment
```
python cli.py --env "config.Testing" run
```

Login to
[http://0.0.0.0:5000/graphql](http://0.0.0.0:5000/graphql)

Server already in use?

```
lsof -i tcp:5000
kill -9 [PID]
```

Populate the database
```
python cli.py --env "config.Testing" run --thread 1 - populate-database scripts/templates
```