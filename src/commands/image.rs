use image;

pub fn resize_image(file_path: &str, output_path: &str, width: u32, height: u32) {
    let img = image::open(file_path).unwrap();
    let resized_img = img.resize_exact(width, height, image::imageops::FilterType::Nearest);
    resized_img.save(output_path).unwrap();
}
