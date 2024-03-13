use std::fmt::Display;

pub trait NumericToString: Display {}

impl NumericToString for i128 {}
impl NumericToString for i64 {}
impl NumericToString for i32 {}
impl NumericToString for i16 {}
impl NumericToString for i8 {}
impl NumericToString for u128 {}
impl NumericToString for u64 {}
impl NumericToString for u32 {}
impl NumericToString for u16 {}
impl NumericToString for u8 {}
impl NumericToString for f64 {}
impl NumericToString for f32 {}

pub fn format_with_commas<T: NumericToString>(num: T) -> String {
    let num_str = num.to_string();
    let mut result = String::new();

    num_str.chars().rev().enumerate().for_each(|(index, char)| {
        if index % 3 == 0 && index != 0 {
            result.push(',');
        }
        result.push(char);
    });

    result.chars().rev().collect()
}

#[cfg(test)]
fn test_format_with_commas<T: NumericToString>(num: T, expected: &str) {
    assert_eq!(format_with_commas(num), expected);
}

#[test]
fn test_format_with_commas_u128() {
    test_format_with_commas(1_000_000_000, "1,000,000,000");
}

#[test]
fn test_format_with_commas_u64() {
    test_format_with_commas(1_000_000, "1,000,000");
}

#[test]
fn test_format_with_commas_u32() {
    test_format_with_commas(1_000, "1,000");
}

#[test]
fn test_format_with_commas_u16() {
    test_format_with_commas(1_000, "1,000");
}

#[test]
fn test_format_with_commas_u8() {
    test_format_with_commas(1_000, "1,000");
}

#[test]
fn test_format_with_commas_i128() {
    test_format_with_commas(-1_000_000_000, "-1,000,000,000");
}

#[test]
fn test_format_with_commas_i64() {
    test_format_with_commas(-1_000_000, "-1,000,000");
}

#[test]
fn test_format_with_commas_i32() {
    test_format_with_commas(-1_000, "-1,000");
}

#[test]
fn test_format_with_commas_i16() {
    test_format_with_commas(-1_000, "-1,000");
}

#[test]
fn test_format_with_commas_i8() {
    test_format_with_commas(-1_000, "-1,000");
}

#[test]
fn test_format_with_commas_f64() {
    test_format_with_commas(1_000.0, "1,000");
}

#[test]
fn test_format_with_commas_f32() {
    test_format_with_commas(1_000.0, "1,000");
}

#[test]
fn test_format_with_commas_string() {
    test_format_with_commas(1000, "1,000");
}
