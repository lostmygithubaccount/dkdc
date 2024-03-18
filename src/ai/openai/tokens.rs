use tiktoken_rs;

pub fn tokenize(string: &str) -> Vec<usize> {
    let bpe = tiktoken_rs::cl100k_base().unwrap();
    let tokens = bpe.encode_with_special_tokens(string);

    return tokens;
}
