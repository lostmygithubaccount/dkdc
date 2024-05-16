use clap::{Parser, Subcommand};
use dkdc;
use futures;
use reqwest;
use serde_json::{Error, Value};

#[derive(Parser, Debug)]
#[command(version)]
#[command(about = "don't know, don't care", long_about = None)]
#[command(arg_required_else_help = true)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand, Debug)]
enum Commands {
    #[command(about = "AI commands", long_about = None)]
    #[command(arg_required_else_help = true)]
    Ai {
        #[command(subcommand)]
        subcommand: AiCommands,
    },

    #[command(about = "Configure things (config.toml by default)", long_about = None)]
    #[command(aliases = &["c"])]
    Config {
        #[arg(short, long)]
        #[arg(default_value = "false")]
        #[arg(help = "Open the .env file")]
        env: bool,

        #[arg(short, long)]
        #[arg(default_value = "false")]
        #[arg(help = "Open with nvim")]
        vim: bool,
    },

    #[command(about = "Open things", long_about = None)]
    #[command(aliases = &["o"])]
    #[command(arg_required_else_help = false)]
    Open {
        thing: Option<String>,

        #[arg(short, long)]
        #[arg(help = "List the things and aliases")]
        list: bool,
    },

    #[command(about = "Print numbers", long_about = None)]
    Run {
        #[arg(short, long)]
        #[arg(default_value_t = 1_000_000_000)]
        max: u128,

        #[arg(short, long)]
        #[arg(default_value_t = 1_000_000)]
        divisor: u128,
    },

    #[command(about = "Image commands", long_about = None)]
    #[command(arg_required_else_help = true)]
    Image {
        #[command(subcommand)]
        subcommand: ImageCommands,
    },
}

#[derive(Subcommand, Debug)]
enum AiCommands {
    #[command(about = "Tokenize", long_about = None)]
    #[command(arg_required_else_help = true)]
    Tokens {
        #[arg(help = "The message to tokenize")]
        string: Option<String>,

        #[arg(short, long)]
        #[arg(help = "The file to read from")]
        filepath: Option<String>,
    },
    #[command(about = "AI chat", long_about = None)]
    #[command(arg_required_else_help = true)]
    Chat {
        #[arg(help = "The message to send to the AI")]
        message: String,

        #[arg(short, long)]
        #[arg(default_value_t = 1)]
        #[arg(help = "The number of completions to generate")]
        n: u8,

        #[arg(short, long)]
        #[arg(default_value_t = 1024)]
        #[arg(help = "The maximum number of tokens to generate")]
        max_tokens: u32,

        #[arg(short, long)]
        #[arg(default_value = "false")]
        #[arg(help = "Verbose output")]
        verbose: bool,
    },
    #[command(about = "AI classify", long_about = None)]
    #[command(arg_required_else_help = true)]
    Classify {
        #[arg(help = "The message to classify")]
        message: Option<String>,

        #[arg(short, long)]
        #[arg(help = "The file to read from")]
        filepath: Option<String>,

        #[arg(short, long)]
        #[arg(help = "The labels to classify against")]
        labels: String,

        #[arg(short, long)]
        #[arg(default_value = "false")]
        #[arg(help = "Allow none of the above")]
        allow_none: bool,

        #[arg(short, long)]
        #[arg(default_value = "false")]
        #[arg(help = "Verbose output")]
        verbose: bool,

        #[arg(short, long)]
        #[arg(default_value_t = 3)]
        #[arg(help = "The number of completions to generate")]
        n: u8,
    },
}

#[derive(Subcommand, Debug)]
enum ImageCommands {
    #[command(about = "Resize an image", long_about = None)]
    Resize {
        #[arg(short, long)]
        #[arg(default_value = "thumbnail.png")]
        file: String,

        #[arg(short, long)]
        #[arg(default_value = "resized.png")]
        output: String,

        #[arg(short = 'W', long)]
        #[arg(default_value_t = 512)]
        width: u32,

        #[arg(short = 'H', long)]
        #[arg(default_value_t = 512)]
        height: u32,
    },
}

#[allow(unused)]
fn cli() {
    let cli = Cli::parse();

    match cli.command {
        Some(Commands::Ai { subcommand }) => {
            dkdc::utils::env::load_dotenv();
            match subcommand {
                AiCommands::Tokens { string, filepath } => {
                    let string = match string {
                        Some(string) => string,
                        None => {
                            let filepath = filepath.unwrap();
                            let string = dkdc::utils::filesystem::file_to_string(filepath.as_str());
                            string.unwrap()
                        }
                    };
                    dkdc::commands::ai::tokenize(string.as_str());
                }
                AiCommands::Chat {
                    message,
                    n,
                    max_tokens,
                    verbose,
                } => {
                    dkdc::commands::ai::ai_chat(message.as_str(), n, max_tokens, verbose);
                }

                AiCommands::Classify {
                    message,
                    filepath,
                    labels,
                    allow_none,
                    verbose,
                    n,
                } => {
                    let message = match message {
                        Some(message) => message,
                        None => {
                            let filepath = filepath.unwrap();
                            let message =
                                dkdc::utils::filesystem::file_to_string(filepath.as_str());
                            message.unwrap()
                        }
                    };
                    let labels =
                        dkdc::utils::strings::comma_separated_string_to_vec(labels.as_str());
                    dkdc::commands::ai::ai_classify(
                        message.as_str(),
                        labels,
                        allow_none,
                        verbose,
                        Some(n),
                    );
                }
            }
        }
        Some(Commands::Config { vim, env }) => {
            dkdc::commands::config::config_it(vim, env);
        }
        Some(Commands::Open { thing, list }) => {
            let list = thing.is_none() || list;
            dkdc::commands::open::open_it(thing, list);
        }
        Some(Commands::Run { max, divisor }) => {
            dkdc::commands::testing::print_numbers(max, divisor);
        }
        Some(Commands::Image { subcommand }) => match subcommand {
            ImageCommands::Resize {
                file,
                output,
                width,
                height,
            } => {
                dkdc::commands::image::resize_image(file.as_str(), output.as_str(), width, height);
            }
        },
        _ => {
            panic!("impossible!")
        }
    }
}

async fn process_stream(response: reqwest::Response) -> Result<String, Error> {
    let mut full_message = String::new();

    let text = response.text().await.unwrap();
    let events = text.split("\n\n");

    for event in events {
        if event.starts_with("data: ") {
            let data: Value = serde_json::from_str(&event[6..])?;
            if let Some(text) = data["choices"][0]["delta"]["content"].as_str() {
                full_message.push_str(text);
                print!("{}", text);
            }
        }

        if event == "data: [DONE]" {
            break;
        }
    }

    Ok(full_message)
}

#[allow(unused)]
fn wip() {
    dkdc::utils::env::load_dotenv();

    let message = "who are you and what can you do?";

    let client = dkdc::ai::openai::client::AsyncClient::new();
    let mut payload = dkdc::ai::openai::client::ChatCompletionPayload::new(message);
    payload.n = Some(1);
    payload.max_tokens = Some(128);
    payload.stream = Some(true);

    let response = client.call_stream(&payload);

    // let result = match futures::executor::block_on(response) {
    //     Ok(response) => response,
    //     Err(err) => {
    //         eprintln!("Error: {}", err);
    //         return;
    //     }
    // };
    // let result = process_stream(result);

    // update the above code to stream through the incoming data
    // and print it out as it comes in

    let result = match futures::executor::block_on(response) {
        Ok(response) => response,
        Err(err) => {
            eprintln!("Error: {}", err);
            return;
        }
    };

    let result = process_stream(result);
}

// fn process_stream(mut response: Response) -> Result<(), serde_json::Error> {
//     let mut reader = response.bytes_stream().into_blocking_read();
//     let mut buf = Vec::new();
//     let mut byte = [0; 1]; // Buffer to store a single byte.
//
//     while let Ok(bytes_read) = reader.read(&mut byte) {
//         if bytes_read == 0 {
//             break; // End of stream.
//         }
//
//         buf.push(byte[0]);
//         let buf_str = match std::str::from_utf8(&buf) {
//             Ok(v) => v,
//             Err(_) => continue, // Incomplete UTF-8 sequence.
//         };
//
//         if buf_str.ends_with("\n\n") {
//             // End of an event.
//             let events: Vec<&str> = buf_str.split("\n\n").collect();
//             for event in events {
//                 if event.starts_with("data: ") {
//                     let data: Value = serde_json::from_str(&event[6..])?;
//                     if let Some(text) = data["choices"][0]["delta"]["content"].as_str() {
//                         print!("{}", text);
//                     }
//                 }
//             }
//             buf.clear();
//         }
//     }
//
//     println!(); // Ensure the output ends with a newline.
//     Ok(())
// }
//
// #[allow(unused)]
// fn wip() {
//     dkdc::utils::env::load_dotenv();
//
//     let message = "who are you and what can you do?";
//
//     let client = dkdc::ai::openai::client::Client::new();
//     let mut payload = dkdc::ai::openai::client::ChatCompletionPayload::new(message);
//     payload.n = Some(1);
//     payload.max_tokens = Some(128);
//     payload.stream = Some(true);
//
//     let response = client.call_stream(&payload);
//     let result = response.unwrap();
//     if let Err(e) = process_stream(result) {
//         eprintln!("Error processing the stream: {}", e);
//     }
// }

use futures_util::StreamExt;
use serde::Deserialize;
use serde_json::json;
use std::io::Write;

#[derive(Debug, Deserialize)]
struct ChatChunkDelta {
    content: Option<String>,
}

#[derive(Debug, Deserialize)]
struct ChatChunkChoice {
    delta: ChatChunkDelta,
    index: usize,
    finish_reason: Option<String>,
}

#[derive(Debug, Deserialize)]
struct ChatCompletionChunk {
    id: String,
    object: String,
    created: usize,
    model: String,
    choices: Vec<ChatChunkChoice>,
}

async fn wip3() -> Result<(), anyhow::Error> {
    let url = "https://api.openai.com/v1/chat/completions";

    dkdc::utils::env::load_dotenv();

    let api_key = dkdc::utils::env::get_openai_api_key();
    //let api_key = std::env::var("OPENAI_API_KEY")?;

    let body = json!({
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "user",
            "content": "Please list 10 things I might want to bring to a picnic."
        }],
        "stream": true
    });

    let client = reqwest::Client::new();
    let res = client
        .post(url)
        .body(body.to_string())
        .header("Content-Type", "application/json")
        .bearer_auth(api_key)
        .send()
        .await?;
    println!("status = {}", res.status());

    println!("ChatGPT Says:");
    println!();
    let mut stream = res.bytes_stream();
    while let Some(item) = stream.next().await {
        let item = item?;
        let s = match std::str::from_utf8(&item) {
            Ok(v) => v,
            Err(e) => panic!("Invalid UTF-8 sequence: {}", e),
        };

        for p in s.split("\n\n") {
            match p.strip_prefix("data: ") {
                Some(p) => {
                    // Check if the stream is done...
                    if p == "[DONE]" {
                        break;
                    }

                    // Parse the json data...
                    let d = serde_json::from_str::<ChatCompletionChunk>(p)
                        .expect(format!("Couldn't parse: {}", p).as_str());

                    // Is there data?
                    let c = d.choices.get(0).expect("No choice returned");
                    if let Some(content) = &c.delta.content {
                        print!("{}", content);
                    }

                    // Flush stdout as it goes...
                    if let Err(error) = std::io::stdout().flush() {
                        panic!("{}", error);
                    }
                }
                None => {}
            }
        }
    }
    println!("");
    println!("[Done.]");

    Ok(())
}

#[tokio::main]
async fn main() {
    wip3().await;
    //cli();
}

// TODOs
// move library logic out of commands/*
// use just files for library code, expand to directories when it makes sense
// move to async/streaming for chat (https://github.com/a-poor/openai-stream-rust-demo)
// implement interactive chat
// finish up ai/openai:
//   - finish up logit bias
//   - add cast
//   - custom functions for birdbrain
// take a look at implementing ai/claude
//
// remember the method: code, wip testing, command
// we ball
