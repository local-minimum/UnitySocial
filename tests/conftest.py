import importlib.util
from glob import glob
import os

import pytest


@pytest.fixture(scope="session")
def app():
    class Container:
        pass
    container = Container()
    for path in glob(
        os.path.join(os.path.dirname(__file__), os.pardir, 'app', '*.py'),
    ):
        name = os.path.basename(path).split(".", 1)[0]
        if name == "__init__":
            continue
        spec = importlib.util.spec_from_file_location('name', path)
        setattr(container, name, importlib.util.module_from_spec(spec))
        spec.loader.exec_module(getattr(container, name))
    print(dir(container))
    return container
