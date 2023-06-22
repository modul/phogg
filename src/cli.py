#!/usr/bin/env python3
"""
This is PhoGG (Photo Gallery Generator) -
a CLI tool to generate a static site photo gallery.
"""
import argparse
from pathlib import Path

from photo_processor import process_photos, SUPPORTED_OUTPUT_TYPES
from site_generator import create_site_directory, generate_site

### CLI ###

DEFAULT_SITE_CONFIG = "site.toml"
DEFAULT_OUTPUT_FORMAT = "JPEG"
DEFAULT_OUTPUT_QUALITY = 80

def parse_arguments():
    """
    Parse the command line arguments
    """
    parser = argparse.ArgumentParser(
        prog="phogg",
        description="A photo gallery site generator",
    )

    parser.add_argument(
        "--source", "-s",
        help="source directory with your photos",
        metavar="DIRECTORY",
        type=Path,
        required=True)
    parser.add_argument(
        "--destination", "-d",
        help="destination directory for your generated site (will be created)",
        metavar="DIRECTORY",
        type=Path,
        required=True)
    parser.add_argument(
        "--force", "-f",
        help="force overwrite of destination directory if it exists",
        action="store_true")
    parser.add_argument(
        "--config", "-c",
        help=f"site configuration file (default: {DEFAULT_SITE_CONFIG})",
        metavar="FILE",
        type=Path,
        default=DEFAULT_SITE_CONFIG)
    parser.add_argument(
        "--output-format", "-o",
        help=f"output image format (default: {DEFAULT_OUTPUT_FORMAT})",
        metavar="TYPE",
        type=str,
        choices=SUPPORTED_OUTPUT_TYPES,
        default=DEFAULT_OUTPUT_FORMAT)
    parser.add_argument(
        "--output-quality", "-q",
        help=f"output image compression quality (default: {DEFAULT_OUTPUT_QUALITY})",
        metavar="TYPE",
        type=int,
        choices=range(0, 101),
        default=DEFAULT_OUTPUT_QUALITY)

    return parser.parse_args()

if __name__ == "__main__":
    arguments = parse_arguments()
    try:
        destination = create_site_directory(arguments.destination, arguments.force)
        photos = process_photos(
            arguments.source,
            destination,
            arguments.output_format,
            arguments.output_quality)
        generate_site(arguments.config, photos, destination)
    except Exception as error:
        print(error)
        print("Aborted")
    else:
        print("Done")
