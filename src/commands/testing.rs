use crate::utils;

pub fn print_numbers(max: u128, divisor: u128) {
    let mut i: u128 = 0;
    loop {
        if i % divisor == 0 {
            println!("i: {}", utils::numeric::format_with_commas(i));
        }
        i += 1;

        if i > max {
            break;
        }
    }
}
