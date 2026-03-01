import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(page_title="Wayne State RAG", layout="centered")

st.title("Wayne State University RAG Assistant")

question = st.text_input("Ask a question")

if st.button("Submit"):
    if question:
        with st.spinner("Thinking..."):
            response = requests.post(
                API_URL,
                json={"question": question}
            )
            
            if response.status_code == 200:
                answer = response.json()["answer"]
                st.markdown("### Answer")
                st.write(answer)
            else:
                st.error("Backend error.")