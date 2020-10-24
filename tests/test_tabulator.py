import numpy as np
import pytest
from PIL import Image

from src.sbs import tabulator


@pytest.fixture
def grayscale():
    grayscale = (np.random.rand(64, 64) * 255).astype(np.uint8)
    image = Image.fromarray(grayscale)
    return image


@pytest.fixture
def rgb():
    rgb = (np.random.rand(64, 64, 3) * 255).astype(np.uint8)
    image = Image.fromarray(rgb)
    return image


@pytest.fixture
def rgba():
    rgb = (np.random.rand(64, 64, 4) * 255).astype(np.uint8)
    image = Image.fromarray(rgb)
    return image


@pytest.fixture
def get_fixture_values(request):
    def _get_fixture(fixture):
        return request.getfixturevalue(fixture)

    return _get_fixture


testdata = ["grayscale", "rgb", "rgba"]


@pytest.mark.parametrize("image", testdata)
def test_add_border(image, get_fixture_values):
    image = get_fixture_values(image)
    border_width = np.random.randint(0, 10)
    tabulator.add_border(image, border_width)
