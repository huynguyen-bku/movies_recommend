import logging
import atexit

import streamlit as st
from module.recommend import Recommend

# Thiết lập trang phải là lệnh đầu tiên
st.set_page_config(page_title="Movie Recommendation System", layout="wide")


@st.cache_resource
def load_module():
    module_re = Recommend(vector_store='checkpoint',
                          path_movies='data/movies.csv')
    return module_re


module_recommend = load_module()

st.title("🎬 Movie Recommendation System")
st.markdown("""
Welcome to the Movie Recommendation System! 
Simply select your preferences and we'll recommend movies you'll love.
""")
text_input = st.text_area("Enter your text here:")

# Button to generate DataFrame
if st.button("Search"):
    if text_input:
        df = module_recommend.get_recommend(text_input)
        if df is not None:
            st.write(df)
        else:
            st.write("No movies found with the selected criteria.")
    else:
        st.write("Please enter some text.")


def close_logging():
    logging.shutdown()


# Đăng ký hàm close_logging với atexit

atexit.register(close_logging)
