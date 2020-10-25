import argparse
from functools import partial
from pathlib import Path

from .powerpoint import paste_image
from .tabulator import preprocessing, tabulate


def tabulate_image(args):
    if args.output is None:
        args.output = Path("./tabulated")
    args.output.mkdir(exist_ok=True)
    preprocessor = partial(
        preprocessing,
        need_trim_background=args.trim,
        resize_size=args.resize_size,
        border_width=args.border_width,
        need_draw_filename=args.draw,
    )
    tabulate(
        args.input, args.output, args.row, args.col, args.glob_pattern, preprocessor
    )


def paste_images_to_pptx(args):
    paste_image(args.input, args.output, args.title, args.glob_pattern)


def main():
    parser = argparse.ArgumentParser(description="Side By Side.")
    subparsers = parser.add_subparsers()

    # tabulate_image
    parser_tabulate_image = subparsers.add_parser(
        "tabulate_image", help="Arange images in the grid. see `tabulate_image -h`"
    )
    parser_tabulate_image.add_argument("input", type=Path, help="input dir")
    parser_tabulate_image.add_argument(
        "-o", "--output", default=None, type=Path, help="output dir"
    )
    parser_tabulate_image.add_argument("-r", "--row", default=-1, type=int)
    parser_tabulate_image.add_argument("-c", "--col", default=-1, type=int)
    parser_tabulate_image.add_argument(
        "--trim", action="store_true", help="trim background from image."
    )
    parser_tabulate_image.add_argument(
        "--resize_size", nargs="+", type=int, default=None
    )
    parser_tabulate_image.add_argument("--border_width", type=int, default=None)
    parser_tabulate_image.add_argument(
        "--draw", action="store_true", help="Draw filename on top of image."
    )
    parser_tabulate_image.add_argument("-g", "--glob_pattern", default="*.png")
    parser_tabulate_image.set_defaults(handler=tabulate_image)

    # paste)images_to_pptx
    parser_paste_images_to_pptx = subparsers.add_parser(
        "paste_images_to_pptx",
        help="Paste images to pptx. see `paste_images_to_pptx -h`",
    )
    parser_paste_images_to_pptx.add_argument(
        "input", type=Path, help="input directory for tabulated images",
    )
    parser_paste_images_to_pptx.add_argument(
        "-o", "--output", type=Path, help="output powerpoint"
    )
    parser_paste_images_to_pptx.add_argument(
        "--title", type=str, help="Title of presentation."
    )
    parser_paste_images_to_pptx.add_argument("--glob_pattern", default="*.png")
    parser_paste_images_to_pptx.set_defaults(handler=paste_images_to_pptx)

    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
