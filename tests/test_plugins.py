from lostdock.services.plugins import discover_plugins
from pathlib import Path


def test_plugin_loading(tmp_path):
    (tmp_path / "my_plugin.py").write_text(
        "NAME = 'test_plugin'\n"
        "def on_result(result):\n"
        "    return None\n"
    )
    plugins = discover_plugins([tmp_path])
    assert len(plugins) == 1
    assert plugins[0].name == "test_plugin"
    assert plugins[0].has("on_result")
    assert plugins[0].has("on_export") is False
