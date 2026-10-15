from aicommit.config import load_config


def test_config_defaults_match_bedrock_setup(tmp_path):
    config = load_config(str(tmp_path / "missing.toml"))

    assert config.model_id == "amazon.nova-pro-v1:0"
    assert config.max_tokens == 2500


def test_config_can_override_max_tokens(tmp_path):
    config_file = tmp_path / ".aicommit.toml"
    config_file.write_text("max_tokens = 1200\n")

    config = load_config(str(config_file))

    assert config.max_tokens == 1200
