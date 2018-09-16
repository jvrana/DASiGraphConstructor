from dasi import create_app


def test_config():
    assert create_app({'TESTING': True}, config='config.Testing').testing
    assert not create_app({'TESTING': False}, config='config.Testing').testing


def test_config_set_server_name():
    config = {"SERVER_NAME": "myserver:5000"}
    app = create_app(config, config='config.Testing')
