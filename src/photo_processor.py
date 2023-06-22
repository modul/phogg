"""
Photo processing module
"""

from pathlib import Path
from time import time
from typing import Any, BinaryIO, Union

import filetype
from PIL import Image, ExifTags

SUPPORTED_INPUT_TYPES = ["image/jpeg"]
SUPPORTED_OUTPUT_TYPES = ["JPEG", "WEBP"]
TARGET_RESOLUTIONS = [(1920, 1080), (1280, 720), (640, 360), (320, 180)]

Size = tuple[int, int]
MaybeString = Union[str, None]
ExifData = dict[str, Any]
PhotoTitleAndDescription = tuple[MaybeString, MaybeString]

class Photo:
    """ Photo container for template """
    def __init__(self,
            title_and_description: PhotoTitleAndDescription,
            paths: dict[int, Path],
            exif_data: ExifData):
        self._exif = exif_data
        self._paths = paths
        self._sizes = list(self._paths.keys())
        self._sizes.sort()
        self._title, self._description = title_and_description

    @property
    def sizes(self) -> list[int]:
        """ Available image sizes (max-width) """
        return self._sizes

    @property
    def default_size(self) -> int:
        """ Default image size (max-width) """
        return self.sizes[0]

    @property
    def path(self) -> Path:
        """ Image path (default size) """
        return self._paths[self.default_size]

    @property
    def paths(self) -> dict[int, Path]:
        """ Image file paths for different sizes """
        return self._paths

    @property
    def file_name(self) -> str:
        """ Image file name """
        return self.path.name

    @property
    def title(self) -> MaybeString:
        """ Photo title from description file """
        return self._title

    @property
    def description(self) -> MaybeString:
        """ Photo description from description file """
        return self._description

    @property
    def exif(self) -> ExifData:
        """ EXIF metadata """
        return self._exif

    def __str__(self):
        return self.file_name


def is_image(path) -> bool:
    """
    Check if the file is a supported image file type
    """
    kind = filetype.guess(path)
    supported_types = ["image/jpeg"]
    return kind is not None and kind.mime in supported_types

def find_photos(source_dir: Path) -> list[Path]:
    """
    Find all photos in the source directory
    """
    print(f"Searching for photos in {source_dir.name}")
    return [path for path in source_dir.iterdir() if path.is_file() and is_image(path)]

def is_landscape_orientation(image: Image) -> bool:
    """ Check if the image is in landscape orientation """
    return image.width > image.height

def get_limited_size(image: Image, max_size: Size) -> Size:
    """
    Calculate the new size of the image, limited by the given max size, depending on orientation.
    """
    width, height = max_size
    aspect_ratio = image.width / image.height
    if is_landscape_orientation(image):
        return (width, int(width / aspect_ratio))
    return (int(height * aspect_ratio), height)

def resize_image(
        file: BinaryIO,
        target: Path,
        max_size: Size,
        output_format: str,
        quality: int) -> Path:
    """
    Resize the image to the given width and convert to output file format
    """
    assert output_format in SUPPORTED_OUTPUT_TYPES

    new_name = target.with_suffix(f".{output_format.lower()}")
    with Image.open(file) as image:
        new_size = get_limited_size(image, max_size)
        resized = image.resize(new_size, Image.LANCZOS)
        resized.save(new_name, format = output_format, quality = quality)
    return new_name

def create_image_directories(destination_dir) -> dict[int, Path]:
    """
    Create an image directory for every max-width in destination_dir
    and return a record of available widths and their directories
    """
    image_dir = destination_dir / "img"
    max_widths = [res[0] for res in TARGET_RESOLUTIONS]
    target_dirs = [image_dir / str(width) for width in max_widths]
    for target in target_dirs:
        target.mkdir(parents=True)

    return dict(zip(max_widths, target_dirs))

def resize_images(
        file: BinaryIO,
        source: Path,
        destination_dirs: dict[int, Path],
        output_format: str,
        output_quality: int,
        ) -> dict[int, Path]:
    """
    Create a converted and resized copy for each targeted resolution
    """
    print("Creating resized copies ", end="", flush=True)
    for max_width, max_height in TARGET_RESOLUTIONS:
        target = destination_dirs[max_width] / source.name
        resize_image(file, target, (max_width, max_height), output_format, output_quality)
        print(".", end="", flush=True)
    print()

def read_exif(file: BinaryIO) -> ExifData:
    """ Read EXIF data from image file """
    image = Image.open(file)
    exif = image.getexif()
    if exif is not None:
        data = dict((ExifTags.TAGS[k], v) for k, v in exif.items() if k in ExifTags.TAGS)
        return data
    return {}

def read_description_file(photo_path: Path) -> PhotoTitleAndDescription:
    """ Read corresponding description file for photo """
    file_path = photo_path.with_suffix(".txt")
    if file_path.is_file():
        with open(file_path, "r", encoding="utf8") as file:
            lines = file.readlines()
            title = lines[0].strip() if len(lines) > 0 else None
            description = lines[1].strip() if len(lines) > 1 else None
            if title or description:
                print(f"Found title \"{title}\" and {'a' if description else 'no'} description")
            return (title, description)
    return (None, None)

def print_statistics(start: int, photos: list[Photo]) -> None:
    """ Print processing statistics """
    duration = round(time() - start)
    photo_count = len(photos)
    title_count = len([p for p in photos if p.title is not None])
    description_count = len([p for p in photos if p.description is not None])
    line_length = 80

    print("*"*line_length)
    print(f"Processed {photo_count} photos in {duration} seconds.")
    print(f"{title_count} photos had a title and {description_count} of them had a description.")
    print("*"*line_length)

def process_photos(
        source_dir: Path,
        destination_dir: Path,
        output_format: str,
        output_quality: int) -> list[Photo]:
    """
    Scan photo files, read metadata, convert/resize and save to destination
    """
    start = time()
    photos = []
    found_exif_tags = set()
    destination_dirs = create_image_directories(destination_dir)

    for source in find_photos(source_dir):
        print(f"Found {source.name}")
        title_and_description = read_description_file(source)
        with open(source, "rb") as file:
            exif_data = read_exif(file)
            found_exif_tags.update(exif_data.keys())
            resize_images(file, source_dir, destination_dirs, output_format, output_quality)
            photos.append(Photo(title_and_description, destination_dirs, exif_data))

    photos.sort(key=str)
    print_statistics(start, photos)
    return photos
