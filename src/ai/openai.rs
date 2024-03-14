use reqwest;
use serde::{Deserialize, Serialize};
use serde_json;

use crate::ai;
use crate::utils;

#[allow(non_camel_case_types)]
#[derive(Serialize, Deserialize, Debug)]
enum MessageRole {
    system,
    assistant,
    user,
}

#[derive(Serialize, Deserialize, Debug)]
struct Message {
    role: MessageRole,
    content: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct ChatCompletionPayload {
    messages: Vec<Message>,
    model: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    frequency_penalty: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    logit_bias: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    logprobs: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    max_tokens: Option<i32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    n: Option<i32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    presence_penalty: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    response_format: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    seed: Option<i32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    stop: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    stream: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    temperature: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    top_p: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    tools: Option<Vec<serde_json::Value>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    user: Option<String>,
}

impl ChatCompletionPayload {
    fn new(user_message: &str) -> Self {
        let payload = ChatCompletionPayload {
            model: ai::models::GPT4.to_string(),
            messages: vec![
                Message {
                    role: MessageRole::system,
                    content: "You are a helpful chatbot.".to_string(),
                },
                Message {
                    role: MessageRole::user,
                    content: user_message.to_string(),
                },
                Message {
                    role: MessageRole::assistant,
                    content: "The answer (as an integer, and only that integer) is:".to_string(),
                },
            ],
            frequency_penalty: None,
            logit_bias: None,
            logprobs: None,
            max_tokens: Some(40),
            n: Some(1),
            presence_penalty: None,
            response_format: None,
            seed: None,
            stop: None,
            stream: None,
            temperature: Some(1.0),
            top_p: None,
            tools: None,
            user: None,
        };

        payload
    }
}

#[derive(Serialize, Deserialize, Debug)]
struct ChatCompletionResponse {
    choices: Vec<ChatCompletionResponseChoices>,
    created: i64,
    id: String,
    model: String,
    object: String,
    system_fingerprint: String,
    usage: ChatCompletionResponseUsage,
}

#[derive(Serialize, Deserialize, Debug)]
struct ChatCompletionResponseChoices {
    finish_reason: String,
    index: i32,
    logprobs: serde_json::Value,
    message: Message,
}

#[derive(Serialize, Deserialize, Debug)]
struct ChatCompletionResponseUsage {
    completion_tokens: i32,
    prompt_tokens: i32,
    total_tokens: i32,
}

struct Client {
    api_endpoint: String,
    client: reqwest::blocking::Client,
    openai_api_key: String,
}

impl Client {
    fn new() -> Self {
        let client = Client {
            api_endpoint: ai::endpoints::OPENAI_CHAT_COMPLETIONS.to_string(),
            client: reqwest::blocking::Client::new(),
            openai_api_key: utils::env::get_openai_api_key(),
        };

        client
    }

    fn call(&self, payload: &ChatCompletionPayload) -> Option<ChatCompletionResponse> {
        let result = self
            .client
            .post(&self.api_endpoint)
            .header("Content-Type", "application/json")
            .header("Authorization", format!("Bearer {}", self.openai_api_key))
            .json(payload)
            .send();

        match result {
            Ok(response) => {
                let response_obj: ChatCompletionResponse = response.json().unwrap();
                Some(response_obj)
            }
            Err(e) => {
                eprintln!("Request failed: {}", e);
                None
            }
        }
    }
}

pub fn chat_completions(user_message: &str) {
    let client = Client::new();
    let mut payload = ChatCompletionPayload::new(user_message);
    payload.n = Some(3);
    let response = client.call(&payload);

    match response {
        Some(response) => {
            for (i, choice) in response.choices.iter().enumerate() {
                println!("Response {}: {}", i, choice.message.content);
            }

            let pretty = serde_json::to_string_pretty(&response).unwrap();
            println!("{}", pretty);
        }
        None => {
            eprintln!("Failed to get a response from the OpenAI API.");
        }
    }
}
