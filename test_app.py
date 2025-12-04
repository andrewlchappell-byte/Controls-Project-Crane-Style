import streamlit as st
import matplotlib.pyplot as plt
st.title("Testing")


first, second = st.columns(2)

with first:
    chosen = st.radio("sorting hat", ("Gryffindaor", "Ravenclaw", "Hufflepuff", "Slytherin"))

with second:
    st.button("Button1")
    figure = plt.figure()
    st.selectbox("Box1", [1, 2, 3])
    st.checkbox("Option")

with st.sidebar:
    st.write("Test")
    st.radio("tt", (1, 2, 3))

tab1, tab2, tab3 = st.tabs(("1", "2", "3"))

with st.page