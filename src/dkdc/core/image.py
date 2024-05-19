from PIL import Image


def resize_image(input_path: str, output_path: str, height: int, width: int) -> None:
    """
    Resize an image.
    """
    with Image.open(input_path) as img:
        resized_img = img.resize((height, width))
        resized_img.save(output_path)
