import streamlit as st
from groq import Groq


def get_groq_api_key():
    """
    Gets the Groq API key from Streamlit secrets.
    Returns None if the key is missing.
    """
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return None


def is_llm_available():
    """
    Checks if Groq API key is available.
    """
    api_key = get_groq_api_key()
    return api_key is not None and api_key.strip() != ""


def ask_llm(prompt, system_message=None, temperature=0.2):
    """
    Sends a prompt to Groq and returns the LLM response as text.
    """

    api_key = get_groq_api_key()

    if api_key is None:
        return None

    client = Groq(api_key=api_key)

    if system_message is None:
        system_message = (
            "You are a helpful AI assistant for a recruiter-facing hiring analysis tool. "
            "Be structured, practical, and recruiter-friendly."
        )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=temperature
    )

    return response.choices[0].message.content