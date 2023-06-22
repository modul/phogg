"""
Website generator module
"""

import shutil
from pathlib import Path

import toml
import jinja2

from photo_processor import Photo

TEMPLATE_INDEX_FILE_NAME = "index.jinja"
SYSTEM_TEMPLATE_PATH = Path(__file__).parent.parent / "templates"
SYSTEM_DEFAULT_TEMPLATES = list(SYSTEM_TEMPLATE_PATH.glob("*"))

def read_config(path: Path):
    """ Parse the site configuration file """
    print(f"Reading site configuration file {path.name}")
    with open(path, "r", encoding="utf8") as file:
        return toml.load(file)

def copy_static_files(template_dir: Path, destination_dir: Path):
    """ Copy static template files to the destination directory """
    static_dir = template_dir / "static"
    static_files = ", ".join(p.name for p in static_dir.iterdir())
    print(f"Copying static template files {static_files}")
    shutil.copytree(static_dir, destination_dir, dirs_exist_ok=True)

def load_template(environment: jinja2.Environment):
    """ Load template file """
    try:
        template = environment.get_template(TEMPLATE_INDEX_FILE_NAME)
        return template
    except FileNotFoundError as exc:
        raise OSError(
            f"no {TEMPLATE_INDEX_FILE_NAME} found in template"
        ) from exc

def create_site_directory(path: Path, force: bool):
    """ Create the destination directory if it doesn't exist """
    print(f"Creating destination directory {path}{' (forcing cleanup)' if force else ''}")
    if path.exists():
        if force:
            shutil.rmtree(path)
        else:
            raise IOError(f"{path} already exists")

    path.mkdir(parents=True)
    return path

def generate_site(
        config_path: Path,
        photos_meta: list[Photo],
        destination_dir: Path
    ):
    """ Render the site template with the given arguments """
    system_template_name = SYSTEM_DEFAULT_TEMPLATES[0].name

    print(f"Loading template {system_template_name}")
    template_dir = SYSTEM_TEMPLATE_PATH / system_template_name
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=True)
    template = load_template(environment)
    site_config = read_config(config_path)

    print("Rendering template")
    with open(destination_dir / "index.html", "w", encoding="utf8") as file:
        result = template.render(
            **site_config,
            photos=photos_meta)
        file.write(result)

    copy_static_files(template_dir, destination_dir)
