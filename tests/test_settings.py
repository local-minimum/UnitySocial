import pytest
from io import StringIO
import app.settings


@pytest.fixture
def empty_settings():
    settings = StringIO()
    return settings


def test_discover_active_services_if_no_games(empty_settings):
    settings = app.settings.Settings(empty_settings)
    assert settings.discover_active_services() == {}
