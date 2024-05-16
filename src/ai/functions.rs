use std::collections::HashMap;

use crate::ai;
use crate::utils;

pub fn chat(user_message: &str, n: u8, max_tokens: u32, verbose: bool) -> String {
    let client = ai::openai::client::Client::new();
    let mut payload = ai::openai::client::ChatCompletionPayload::new(user_message);
    payload.n = Some(n);
    payload.max_tokens = Some(max_tokens);
    let response = client.call(&payload);

    match response {
        Some(response) => {
            let mut output = String::new();
            for (i, choice) in response.choices.iter().enumerate() {
                let message = utils::strings::format_string_with_line_limit(
                    choice.message.content.as_str(),
                    None,
                );
                if verbose {
                    println!("Response {}:\n{}", i, message);
                }
                output.push_str(format!("Response {}:\n{}", i, message,).as_str());
            }

            if verbose {
                let pretty = serde_json::to_string_pretty(&response).unwrap();
                println!("{}", pretty);
            }

            output
        }
        None => {
            eprintln!("Failed to get a response from the OpenAI API.");

            String::from("Failed to get a response from the OpenAI API.")
        }
    }
}

pub fn classify(
    text: &str,
    mut labels: Vec<&str>,
    allow_none: bool,
    verbose: bool,
    n: Option<u8>,
) -> String {
    if allow_none {
        labels.push("None of the above");
    }

    let client = ai::openai::client::Client::new();
    let mut logit_bias: HashMap<i64, f32> = HashMap::new();

    for (i, _) in labels.iter().enumerate() {
        logit_bias.insert(
            ai::openai::tokens::tokenize(format!("{}", i).as_str())[0] as i64,
            100.0,
        );
    }

    let text = format!(
        "{}\nChoices:\n  {}",
        text,
        labels
            .iter()
            .enumerate()
            .map(|(i, label)| format!("{}: {}", i, label))
            .collect::<Vec<String>>()
            .join("\n  ")
    );

    if verbose {
        println!("Text: {}", text);
    }

    let mut payload = ai::openai::client::ChatCompletionPayload::new(text.as_str());
    payload.max_tokens = Some(1);
    payload.logit_bias = Some(logit_bias);
    payload.n = Some(n.unwrap_or(3));

    let response = client.call(&payload);

    let mut votes: HashMap<usize, u8> = HashMap::new();

    match response {
        Some(response) => {
            for (i, choice) in response.choices.iter().enumerate() {
                if verbose {
                    println!("Response {}:\n{}", i, choice.message.content);
                    println!(
                        "Chose category: {}",
                        labels[choice.message.content.parse::<usize>().unwrap()]
                    );
                }

                let category = choice.message.content.parse::<usize>().unwrap();
                let count = votes.entry(category).or_insert(0);
                *count += 1;
            }

            if verbose {
                let pretty = serde_json::to_string_pretty(&response).unwrap();
                println!("{}", pretty);
            }
        }
        None => {
            eprintln!("Failed to get a response from the OpenAI API.");
        }
    }

    let (max_label, _) = votes.iter().max_by(|a, b| a.1.cmp(b.1)).unwrap_or((&0, &0));

    labels[*max_label].to_string()
}

pub fn cast() {
    todo!()
}

pub fn extract() {
    todo!()
}
