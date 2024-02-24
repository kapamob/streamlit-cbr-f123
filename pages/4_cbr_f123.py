import streamlit as st
from streamlit.logger import get_logger

import urllib.request
import rarfile
import subprocess
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
    r.extract('122023_123D.dbf')
    st.write('ok')
    
    r.extract("122023_123B.dbf")
    
    # класс для правильного разбора ф.123
    # https://github.com/olemb/dbfread/issues/20#issuecomment-490289235
    class MyFieldParser(FieldParser):
        def parseN(self, field, data):
            data = data.strip().strip(b'*\x00')  # Had to strip out the other characters first before \x00, as per super function specs.
            return super(MyFieldParser, self).parseN(field, data)
    
        def parseD(self, field, data):
            data = data.strip(b'\x00')
            return super(MyFieldParser, self).parseD(field, data)
    
    # Load content of a DBF file into a Pandas data frame
    dbf = DBF('/content/122023_123D.dbf', parserclass=MyFieldParser)
    frame = DataFrame(iter(dbf))
    zero = frame[frame['C1'] == '000'] #создаем фрейм в который загоняем только строку 000 - с итоговым значением капитала
    
    # загружаем файл с названиями банков
    dbf2 = DBF('/content/122023_123B.dbf', parserclass=MyFieldParser, encoding='cp866')
    frame2 = DataFrame(iter(dbf2))
    frame3 = frame2[['REGN','NAME_B']]
    zero=zero.merge(frame3, how = 'left')
    print(zero.sort_values('C3', ascending=[False]).head(20))
    st.write('st.table')
    st.table(zero)
    
if __name__ == "__main__":
    run()
