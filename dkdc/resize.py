# imports
import typer
import logging as log
from rich import print
from PIL import Image

# configure logger
log.basicConfig(level=log.INFO)


def resize_image(
    filename: str = "thumbnail.png", output: str = "thumbnail", size: int = 256
):
    try:
        # Open the image file
        img = Image.open(filename)

        # Calculate the new height while maintaining the aspect ratio
        width, height = img.size
        new_width = size
        new_height = int(height * new_width / width)

        # Resize the image
        resized_img = img.resize((new_width, new_height))

        # Overwrite the original image file
        resized_img.save(output)

        log.info(
            f"Image resized successfully. New dimensions: {new_width}x{new_height}"
        )
        log.info(f"Output file: {output}")
    except FileNotFoundError:
        log.error("File not found.")


# functions
