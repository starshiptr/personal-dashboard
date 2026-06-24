import streamlit as st

st.title("personal Dashboard:")
count = 0 
if st.button("add One"):
    count = count + 1

st.write("Count:", count)
