import numpy as np
from PIL import Image

from src.sbs.powerpoint import PowerPoint, SlideMaster


def test_powerpoint():
    ppt = PowerPoint()
    assert len(ppt.slide_layouts) == len(SlideMaster)


def test_add_title():
    ppt = PowerPoint()
    ppt.add_title(title="title", name="name")


def test_add_contents():
    ppt = PowerPoint()
    ppt.add_contents(title="title", contents="contents")


def test_add_image():
    ppt = PowerPoint()
    # square
    image = Image.fromarray((np.random.rand(64, 64) * 255).astype(np.uint8))
    ppt.add_image(image)

    # rectangle
    image = Image.fromarray((np.random.rand(96, 48) * 255).astype(np.uint8))
    ppt.add_image(image)
    image = Image.fromarray((np.random.rand(48, 96) * 255).astype(np.uint8))
    ppt.add_image(image)
