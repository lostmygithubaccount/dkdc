use image;
use image::error::ImageError;

pub fn resize_image(
    file_path: &str,
    output_path: &str,
    width: u32,
    height: u32,
) -> Result<(), ImageError> {
    let img = image::open(file_path)?;
    let resized_img = img.resize_exact(width, height, image::imageops::FilterType::Nearest);
    resized_img.save(output_path)?;
    Ok(())
}
