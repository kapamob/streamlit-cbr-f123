
import streamlit as st
from streamlit.logger import get_logger

import urllib.request
import rarfile
from io import BytesIO
from dbfread import DBF, FieldParser, InvalidValue
from pandas import DataFrame

LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    st.write("# Капитал банка по ф.123")

    st.markdown(
        """
        
    """
    )



    resp = urllib.request.urlopen('https://www.cbr.ru/vfs/credit/forms/123-20240101.rar')
    r = rarfile.RarFile(BytesIO(resp.read()))
    r.namelist()
    r.extract("122023_123D.dbf")
    st.write('ok')


if __name__ == "__main__":
    run()
