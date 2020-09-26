import platform
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


def add_border(
    img: Image.Image,
    border: Union[int, Tuple[int, ...]],
    color: Tuple[int, ...] = (128, 128, 128),
) -> Image.Image:
    if isinstance(border, int) or isinstance(border, tuple):
        border_img = ImageOps.expand(img, border=border, fill=color)
    else:
        raise RuntimeError("Border is not an integer or tuple")
    return border_img


def crop_image(im: Image.Image) -> Image.Image:
    im_rgb = im.convert("RGB")
    im_background = Image.new("RGB", im_rgb.size, im_rgb.getpixel((0, 0)))
    diff = ImageChops.difference(im_rgb, im_background)
    croprange = diff.convert("RGB").getbbox()
    if croprange is None:
        return im
    return im.crop(croprange)


def resize_image(
    im: Image.Image, size: Tuple[int, ...], keep_aspect: bool = True
) -> Image.Image:
    if keep_aspect:
        im.thumbnail(size, Image.ANTIALIAS)
    else:
        im = im.resize(size, Image.ANTIALIAS)
    result_image = Image.new(im.mode, size, (0, 0, 0, 255))
    result_image.paste(im, ((size[0] - im.size[0]) // 2, (size[1] - im.size[1]) // 2))
    return result_image


def get_font():
    pf = platform.system()
    if pf == "Windows":
        return "C:/Windows/fonts/Times New Roman/times.ttf"
    if pf == "Darwin":
        return "/Library/Fonts/Arial Unicode.ttf"
    if pf == "Linux":
        return "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf"
    # if wsl
    # "/mnt/c/Windows/Fonts/times.ttf"


def draw_text(
    img: Image.Image, text: Optional[str] = None, text_color=(0, 0, 0)
) -> Image.Image:
    if text is None:
        return img
    img_size = img.size
    font_size = img.size[1] // 16  # 8 is manual parameter
    crop_range = np.array(img.getbbox())
    crop_range[1] -= font_size
    img = img.crop(crop_range)
    draw = ImageDraw.Draw(img)
    draw.font = ImageFont.truetype(get_font, font_size)
    text_size = draw.font.getsize(text)
    pos = ((img_size[0] - text_size[0]) // 2, 0)
    pos = (0, 0)
    draw.text(pos, text, text_color)
    return img


def path2image(path: Path) -> Image.Image:
    return Image.open(str(path))


def concatenate_images(images: List[Image.Image], mode: str) -> Image.Image:
    assert isinstance(images, list), "is not list"
    assert isinstance(images[0], Image.Image), "is not PIL.Image"
    assert mode in ["vertical", "horizontal"], "must select concatenating direction"
    sizes = [image.size for image in images]
    if mode == "vertical":
        size = np.max(sizes, axis=0)[0], np.sum(sizes, axis=0)[1]
    else:
        size = np.sum(sizes, axis=0)[0], np.max(sizes, axis=0)[1]
    new_image = Image.new(images[0].mode, tuple(size))
    offset = 0
    for i, image in enumerate(images):
        new_image.paste(image, (0, offset) if mode == "vertical" else (offset, 0))
        offset += sizes[i][1] if mode == "vertical" else sizes[i][0]
    return new_image


def tabulate_image(row: int, col: int, images: List[Image.Image]) -> List[Image.Image]:
    assert isinstance(row, int)
    assert isinstance(col, int)
    num_images = len(images)
    num_sheets = num_images // row // col
    # Create a list of indexes needed to create a row x col sheet
    indices = list(range(0, num_images, col))
    if indices[-1] != num_images:
        indices.append(num_images)
    tabulated_images = []
    for sheet in range(num_sheets + 1):
        tabulated_image = []
        for vertical in range(row):
            try:
                index = {
                    "begin": indices[sheet * row + vertical],
                    "end": indices[sheet * row + vertical + 1],
                }
            except IndexError:
                # When there are not enough images to fill the columns.
                continue
            tabulated_image.append(
                concatenate_images(images[index["begin"] : index["end"]], "horizontal")
            )
        if not tabulated_image:
            continue
        im = concatenate_images(tabulated_image, "vertical")
        tabulated_images.append(im)
    return tabulated_images


def preprocessing(
    image_path: Path,
    need_crop: bool = False,
    resize_size: Optional[Iterable[int]] = None,
    need_border: bool = False,
    need_draw_filename: bool = False,
) -> Image.Image:
    assert isinstance(image_path, Path), "is not path"
    image = path2image(image_path)
    if need_crop:
        image = crop_image(image)
    if resize_size is not None:
        assert isinstance(resize_size, (list, tuple))
        assert len(resize_size) == 2
        image = resize_image(image, tuple(resize_size))
    if need_border:
        image = add_border(image, border=(5, 0))
    if need_draw_filename:
        image = draw_text(image, image_path.stem, text_color=(1, 1, 1))
    return image


def tabulate(
    input_dir: Path,
    output_dir: Path,
    row: int,
    col: int,
    glob_pattern: str = "*.png",
    preprocessor=None,
) -> None:
    if preprocessor is None:
        preprocessor = preprocessing
    image_files = list(input_dir.glob(glob_pattern))
    num_digits = len(str(len(image_files)))

    images: List[Image.Image] = []
    for file in image_files:
        images.append(preprocessor(file))
    images_tabulated = tabulate_image(row, col, images)

    for i, image in enumerate(images_tabulated):
        image.save(output_dir / f"tabulated_{i:0{num_digits}d}.png")
