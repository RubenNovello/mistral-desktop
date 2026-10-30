//! mistral-desktop-core — core di streaming ad alte prestazioni per Mistral Desktop.
//!
//! Espone due funzioni Python via PyO3:
//!   ollama_stream(host, model, messages, temperature, callback)
//!   mistral_stream(api_key, model, messages, temperature, callback)
//!
//! Build (dalla root del progetto, con `maturin`):
//!   pip install maturin
//!   maturin build --release
//!   pip install target/wheels/mistral_desktop_core-*.whl

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyAny;

use std::io::{BufRead, BufReader};

/// Converte una lista Python di dict {role, content} in JSON.
fn messages_to_json(messages: &Bound<'_, PyAny>) -> PyResult<String> {
    let mut out = String::from("[");
    let len = messages.len()?;
    for i in 0..len {
        let m = messages.get_item(i)?;
        let role: String = m.get_item("role")?.extract()?;
        let content: String = m.get_item("content")?.extract()?;
        out.push_str(&format!(
            "{{\"role\":{},\"content\":{}}}",
            serde_json::to_string(&role).unwrap(),
            serde_json::to_string(&content).unwrap()
        ));
        if i + 1 < len {
            out.push(',');
        }
    }
    out.push(']');
    Ok(out)
}

/// Legge la risposta HTTP riga per riga e invia ogni pezzo alla callback Python.
fn stream_lines(
    response: Result<ureq::Response, ureq::Error>,
    is_sse: bool,
    callback: &Bound<'_, PyAny>,
) -> PyResult<()> {
    let resp = response.map_err(|e| PyRuntimeError::new_err(format!("HTTP: {e}")))?;
    let reader = resp.into_reader();
    for line in BufReader::new(reader).lines() {
        let line = line.map_err(|e| PyRuntimeError::new_err(format!("IO: {e}")))?;
        let payload = if is_sse {
            match line.strip_prefix("data: ") {
                Some(p) => p.trim().to_string(),
                None => continue,
            }
        } else {
            line
        };
        if payload.is_empty() || payload == "[DONE]" {
            continue;
        }
        let v: serde_json::Value = match serde_json::from_str(&payload) {
            Ok(v) => v,
            Err(_) => continue,
        };
        let piece = if is_sse {
            v["choices"][0]["delta"]["content"].as_str().unwrap_or("")
        } else {
            v["message"]["content"].as_str().unwrap_or("")
        };
        if !piece.is_empty() {
            callback.call1((piece,))?;
        }
    }
    Ok(())
}

/// Streaming da Ollama locale (endpoint /api/chat, una riga JSON per token).
#[pyfunction]
fn ollama_stream(
    host: String,
    model: String,
    messages: &Bound<'_, PyAny>,
    temperature: f64,
    callback: &Bound<'_, PyAny>,
) -> PyResult<()> {
    let body = format!(
        "{{\"model\":{},\"messages\":{},\"stream\":true,\"options\":{{\"temperature\":{}}}}}",
        serde_json::to_string(&model).unwrap(),
        messages_to_json(messages)?,
        temperature
    );
    let resp = ureq::post(format!("{host}/api/chat").as_str())
        .set("Content-Type", "application/json")
        .send_string(&body);
    stream_lines(resp, false, callback)
}

/// Streaming dall'API Mistral (endpoint /v1/chat/completions, SSE).
#[pyfunction]
fn mistral_stream(
    api_key: String,
    model: String,
    messages: &Bound<'_, PyAny>,
    temperature: f64,
    callback: &Bound<'_, PyAny>,
) -> PyResult<()> {
    let body = format!(
        "{{\"model\":{},\"messages\":{},\"stream\":true,\"temperature\":{}}}",
        serde_json::to_string(&model).unwrap(),
        messages_to_json(messages)?,
        temperature
    );
    let resp = ureq::post("https://api.mistral.ai/v1/chat/completions")
        .set("Authorization", format!("Bearer {api_key}").as_str())
        .set("Content-Type", "application/json")
        .send_string(&body);
    stream_lines(resp, true, callback)
}

#[pymodule]
fn mistral_desktop_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ollama_stream, m)?)?;
    m.add_function(wrap_pyfunction!(mistral_stream, m)?)?;
    Ok(())
}
