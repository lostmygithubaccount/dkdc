use crate::ai;

pub fn tokenize(user_message: &str) {
    let tokens = ai::openai::tokens::tokenize(user_message);

    println!("Tokens: {:?}", tokens);
    println!("Num tokens: {}", tokens.len());
}

pub fn ai_chat(user_message: &str, n: u8, max_tokens: u32, verbose: bool) {
    let response = ai::functions::chat(user_message, n, max_tokens, verbose);
    println!("{}", response);
}

pub fn ai_classify(text: &str, labels: Vec<&str>, allow_none: bool, verbose: bool, n: Option<u8>) {
    let label = ai::functions::classify(text, labels, allow_none, verbose, n);
    println!("Category: {}", label);
}
