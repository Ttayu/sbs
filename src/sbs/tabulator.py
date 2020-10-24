import platform
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


def _is_pil_image(img: Image.Image):
    return isinstance(img, Image.Image)


def _check_tuple_type(value: Tuple[Any], type_: type):
    return isinstance(value, tuple) and all([isinstance(v, type_) for v in value])


def _get_color_list(img: Image.Image, value: int) -> Tuple[int, ...]:
    if img.mode == "L":
        color: Tuple[int, ...] = (value,)
    elif img.mode == "RGB":
        color = (value, value, value)
    elif img.mode == "RGBA":
        color = (value, value, value, value)
    else:
        raise ValueError(f"{img.mode} doesn't support.")
    return color


def add_border(img: Image.Image, border_width: int) -> Image.Image:
    if not _is_pil_image(img):
        raise ValueError(f"img must be PIL.Image, got {type(img)}")
    color = _get_color_list(img, 0)

    border_img = ImageOps.expand(img, border=border_width // 2, fill=color)
    return border_img


def trim_background(img: Image.Image) -> Image.Image:
    im_background = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, im_background)
    croprange = diff.getbbox()
    if croprange is None:
        return img
    return img.crop(croprange)


def resize(img: Image.Image, size: Union[int, Tuple[int, int]]) -> Image.Image:
    if isinstance(size, int):
        size = (size, size)
    bg_value = int(np.mean(img))
    enlarge = img.size[0] < size[0] and img.size[1] < size[1]
    if enlarge:
        width, height = img.size
        if width == height:
            new_width = min(size)
            new_height = min(size)
        elif height < width:
            new_width = size[0]
            new_height = int(size[0] * height / width)
        else:
            new_height = size[1]
            new_width = int(size[1] * width / height)
        img = img.resize((new_width, new_height), Image.ANTIALIAS)
    else:
        img.thumbnail(size, Image.ANTIALIAS)
    background_color = (
        bg_value if img.mode == "L" else (bg_value, bg_value, bg_value, 255)
    )
    result_image = Image.new(img.mode, size, background_color)
    result_image.paste(
        img, ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2)
    )
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
    draw.font = ImageFont.truetype(get_font(), font_size)
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
    need_trim_background: bool = False,
    resize_size: Union[int, Tuple[int, int], None] = None,
    border_width: Optional[int] = None,
    need_draw_filename: bool = False,
) -> Image.Image:
    if not isinstance(image_path, Path):
        ValueError(f"image_path must be pathlib.Path objects, got {type(image_path)}")
    image = path2image(image_path)
    if need_trim_background:
        image = trim_background(image)
    if resize_size is not None:
        image = resize(image, resize_size)
    if border_width is not None:
        image = add_border(image, border_width=border_width)
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

    if row < 0 and col < 0:
        row = int(np.sqrt(len(image_files)))
        col = int(np.sqrt(len(image_files)))
    elif row < 0:
        row = int(len(image_files) / col + 0.5)
    elif col < 0:
        col = int(len(image_files) / row + 0.5)

    images: List[Image.Image] = []
    for file in image_files:
        images.append(preprocessor(file))
    images_tabulated = tabulate_image(row, col, images)

    for i, image in enumerate(images_tabulated):
        image.save(output_dir / f"tabulated_{i:0{num_digits}d}.png")
