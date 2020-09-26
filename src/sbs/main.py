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
        need_crop=args.crop,
        resize_size=tuple(args.resize_size),
        need_border=args.border,
        need_draw_filename=args.draw_filename,
    )
    tabulate(args.input, args.output, args.row, args.col, preprocessor=preprocessor)


def paste_images_to_pptx(args):
    paste_image(args.input, args.output, args.title)


def main():
    parser = argparse.ArgumentParser(description="Side By Side.")
    subparsers = parser.add_subparsers()

    # tabulate_image
    parser_tabulate_image = subparsers.add_parser(
        "tabulate_image", help="Arange images in the grid. see `tabulate_image -h`"
    )
    parser_tabulate_image.add_argument(
        "-i", "--input", type=Path, required=True, help="input dir"
    )
    parser_tabulate_image.add_argument(
        "-o", "--output", default=None, type=Path, help="output dir"
    )
    parser_tabulate_image.add_argument("-r", "--row", default=-1, type=int)
    parser_tabulate_image.add_argument("-c", "--col", default=-1, type=int)
    parser_tabulate_image.add_argument("--crop", action="store_true")
    parser_tabulate_image.add_argument(
        "--resize_size", nargs="+", type=int, default=None
    )
    parser_tabulate_image.add_argument("--border", action="store_true")
    parser_tabulate_image.add_argument("--draw_filename", action="store_true")
    parser_tabulate_image.set_defaults(handler=tabulate_image)

    # paste)images_to_pptx
    parser_paste_images_to_pptx = subparsers.add_parser(
        "paste_images_to_pptx",
        help="Paste images to pptx. see `paste_images_to_pptx -h`",
    )
    parser_paste_images_to_pptx.add_argument(
        "-i",
        "--input",
        type=Path,
        required=True,
        help="input directory for tabulated images",
    )
    parser_paste_images_to_pptx.add_argument(
        "-o", "--output", type=Path, help="output powerpoint"
    )
    parser_paste_images_to_pptx.add_argument(
        "--title", type=str, help="Title of presentation."
    )
    parser_paste_images_to_pptx.set_defaults(handler=paste_images_to_pptx)

    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
