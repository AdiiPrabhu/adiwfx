import os
import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Whatfix Salesforce Help Assistant", layout="wide")
st.title("Whatfix Salesforce Help Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


user_input = st.chat_input("Ask anything about Salesforce...")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={"question": user_input},
                    timeout=120  # give the backend up to 2 minutes
                )
                if res.status_code == 200:
                    data = res.json()
                    ans = data["response"]
                    refs = data.get("references", [])
                    conf = data.get("confidence", 0.0)
                    markdown = f"{ans}\n\n**Confidence:** {conf}%"
                    if refs:
                        markdown += "\n\n**References:**\n" + "\n".join(f"- [{u}]({u})" for u in refs)
                    st.markdown(markdown)
                    st.session_state.messages.append({"role":"assistant","content":markdown})
                else:
                    st.error(f"Error from backend: {res.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")
