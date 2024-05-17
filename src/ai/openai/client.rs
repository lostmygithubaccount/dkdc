use reqwest;
use serde::{Deserialize, Serialize};
use serde_json;
use std::collections::HashMap;

use crate::ai;
use crate::utils;

#[allow(non_camel_case_types)]
#[derive(Serialize, Deserialize, Debug)]
pub enum MessageRole {
    system,
    assistant,
    user,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Message {
    pub role: MessageRole,
    pub content: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ChatCompletionPayload {
    pub messages: Vec<Message>,
    pub model: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub frequency_penalty: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub logit_bias: Option<HashMap<i64, f32>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub logprobs: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_tokens: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub n: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub presence_penalty: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub response_format: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub seed: Option<i32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub stop: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub stream: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub temperature: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub top_p: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tools: Option<Vec<serde_json::Value>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub user: Option<String>,
}

impl ChatCompletionPayload {
    pub fn new(user_message: &str) -> Self {
        let payload = ChatCompletionPayload {
            model: ai::openai::models::GPT_4.to_string(),
            messages: vec![
                Message {
                    role: MessageRole::system,
                    content: "You are a helpful chatbot.".to_string(),
                },
                Message {
                    role: MessageRole::user,
                    content: user_message.to_string(),
                },
                // Message {
                //     role: MessageRole::assistant,
                //     content: "The answer is:".to_string(),
                // },
            ],
            frequency_penalty: None,
            logit_bias: None,
            logprobs: None,
            max_tokens: None,
            n: Some(1),
            presence_penalty: None,
            response_format: None,
            seed: None,
            stop: None,
            stream: None,
            temperature: Some(0.0),
            top_p: None,
            tools: None,
            user: None,
        };

        payload
    }
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ChatCompletionResponse {
    pub choices: Vec<ChatCompletionResponseChoices>,
    pub created: i64,
    pub id: String,
    pub model: String,
    pub object: String,
    pub system_fingerprint: String,
    pub usage: ChatCompletionResponseUsage,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ChatCompletionResponseChoices {
    pub finish_reason: String,
    pub index: i32,
    pub logprobs: serde_json::Value,
    pub message: Message,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ChatCompletionResponseUsage {
    pub completion_tokens: i32,
    pub prompt_tokens: i32,
    pub total_tokens: i32,
}

pub struct Client {
    pub api_endpoint: String,
    client: reqwest::blocking::Client,
    openai_api_key: String,
}

impl Client {
    pub fn new() -> Self {
        let client = Client {
            api_endpoint: ai::openai::endpoints::OPENAI_CHAT_COMPLETIONS.to_string(),
            client: reqwest::blocking::Client::new(),
            openai_api_key: utils::env::get_openai_api_key(),
        };

        client
    }

    pub fn call(&self, payload: &ChatCompletionPayload) -> Option<ChatCompletionResponse> {
        let result = self
            .client
            .post(&self.api_endpoint)
            .header("Content-Type", "application/json")
            .header("Authorization", format!("Bearer {}", self.openai_api_key))
            .json(payload)
            .send();

        match result {
            Ok(response) => {
                // TODO: better error handling
                // e.g. using 'gpt-4-turbo-preview' as the model
                // started failing without a good explanation
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

pub fn chat_completions(user_message: &str, n: u8, max_tokens: u32, verbose: bool) {
    let client = Client::new();
    let mut payload = ChatCompletionPayload::new(user_message);
    payload.n = Some(n);
    payload.max_tokens = Some(max_tokens);
    let response = client.call(&payload);

    match response {
        Some(response) => {
            for (i, choice) in response.choices.iter().enumerate() {
                println!(
                    "Response {}:\n{}",
                    i,
                    utils::strings::format_string_with_line_limit(
                        choice.message.content.as_str(),
                        None
                    )
                );
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
}
