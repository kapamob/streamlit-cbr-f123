import streamlit as st
from streamlit.logger import get_logger
import urllib.request
import urllib.error
import rarfile
from io import BytesIO
from dbfread import DBF, FieldParser, InvalidValue
from pandas import DataFrame
from streamlit.hello.utils import show_code

LOGGER = get_logger(__name__)

def cbr_f123():
    st.set_page_config(page_title="Капитал банков по ф.123", page_icon="📊")
    st.sidebar.header("Капитал банков")

    st.write("# Капитал банков по ф.123")
    st.text("Выберите дату, за которую нужно отобразить данные.")

    v_year = st.selectbox("Год",list(reversed(range(2021,2025))))
    v_month = st.selectbox("Месяц",list(range(1,13)))
    
    if v_month == 12:
        v_file = str(v_month) + str(v_year)
        v_year = v_year+1
        v_url_date = str(v_year) + "0101"
        v_txt_date = "01.01." + str(v_year)
    if v_month > 9 and v_month < 12:
        v_file = str(v_month) + str(v_year)
        v_month = v_month+1
        v_url_date = str(v_year) + str(v_month) + "01"
        v_txt_date = "01." + str(v_month) + "." + str(v_year)
    if v_month == 9:
        v_file = "0" + str(v_month) + str(v_year)
        v_month = v_month+1
        v_url_date = str(v_year) + str(v_month) + "01"
        v_txt_date = "01." + str(v_month) + "." + str(v_year)
    if v_month < 9:
        v_file = "0" + str(v_month) + str(v_year)
        v_month = v_month+1
        v_url_date = str(v_year) + "0" + str(v_month) + "01"
        v_txt_date = "01.0" + str(v_month) + "." + str(v_year)

    v_num = st.slider('Количество банков в списке:', 0, 1000, 15)
    v_file_b=v_file + "_123B.dbf"
    v_file_d=v_file + "_123D.dbf"
    v_url = "https://www.cbr.ru/vfs/credit/forms/123-" + v_url_date + ".rar"
    v_url2 = "https://www.cbr.ru/vfs/credit/forms/123-20240101.rar"
    v_try = 0

    try:
        with urllib.request.urlopen(v_url) as resp:
            r = rarfile.RarFile(BytesIO(resp.read()))
            st.text ("Капитал банков на " + v_txt_date + " г.")
    except urllib.error.URLError:
        st.text ("Данные на выбранную дату недоступны. Попытка вывести данные на 01.01.2024 г.")
        v_try = 1
    
    if v_try == 1:   
        try:
            with urllib.request.urlopen(v_url2) as resp:
                r = rarfile.RarFile(BytesIO(resp.read()))
                v_file_b = "122023_123B.dbf"
                v_file_d = "122023_123D.dbf"
                st.text ("Не найдены данные за выбранную дату")
                st.text ("Капитал банков на 01.01.2024 г.")
                #st.text (v_url2)
        except urllib.error.URLError:
            st.text ("Данные на 01.01.2024 г. недоступны.")
            st.text ("К сожалению cbr.ru блокирует доступ к сайту при большом количестве запросов. Попробуйте позже")
            v_try = 2      
    
    if v_try != 2:
        r.extract(v_file_b)
        r.extract(v_file_d)
   
        # special class for correct parsing f123 from dbf. source: https://github.com/olemb/dbfread/issues/20#issuecomment-490289235
        class MyFieldParser(FieldParser):
            def parseN(self, field, data):
                data = data.strip().strip(b'*\x00')  # Had to strip out the other characters first before \x00, as per super function specs.
                return super(MyFieldParser, self).parseN(field, data)

            def parseD(self, field, data):
                data = data.strip(b'\x00')
                return super(MyFieldParser, self).parseD(field, data)
   
        # load content of a dbf file into a Pandas data frame
        dbf = DBF(v_file_d, parserclass=MyFieldParser)
        df = DataFrame(iter(dbf))
        df = df[df['C1'] == '000'] #create frame with specific row - '000' that contains the total value of capital
            
        # load content of a dbf file into a Pandas data frame
        dbf_names = DBF(v_file_b, parserclass=MyFieldParser, encoding='cp866')
        df_names = DataFrame(iter(dbf_names))
        df_names = df_names[['REGN','NAME_B']]
        df = df.merge(df_names, how = 'left')
        df = df.sort_values(by = "C3", ascending = [False]).head(v_num)
        df.insert(0, "RANK", range(1, 1 + len(df)))
        st.dataframe(data=df, hide_index=True)
        #st.dataframe(data = df, column_order = ('RANK','REGN','NAME_B','C3'), column_config = {'RANK':'№', 'REGN':'Рег.номер', 'NAME_B':'Наименование банка', 'C3':'Значение капитала'}, hide_index = True)
        st.dataframe(data=df, column_order=("RANK","REGN","NAME_B","C3"), column_config={"RANK":"№", "REGN":"Рег.номер", "NAME_B":"Наименование банка", "C3":"Значение капитала"}, hide_index=True)
    st.text("Источник данных: https://www.cbr.ru/banking_sector/otchetnost-kreditnykh-organizaciy/")
    st.text("Репозиторий: https://github.com/kapamob/streamlit-cbr-f123")


cbr_f123()

show_code(cbr_f123)

