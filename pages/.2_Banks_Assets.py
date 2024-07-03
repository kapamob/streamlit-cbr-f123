import streamlit as st
from streamlit.logger import get_logger
import urllib.request
import urllib.error
import rarfile
from io import BytesIO
from dbfread import DBF, FieldParser, InvalidValue
from pandas import DataFrame, merge
from streamlit.hello.utils import show_code

LOGGER = get_logger(__name__)

def cbr_f123():
    st.set_page_config(page_title="Активы банков по ф.101", page_icon="📊")
    st.sidebar.header("Активы банков")

    st.write("# Активы банков по ф.101")
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
    v_file_b=v_file + "N1.dbf"
    v_file_d=v_file + "B1.dbf"
    v_url = "https://www.cbr.ru/vfs/credit/forms/101-" + v_url_date + ".rar"
    v_url2 = "https://www.cbr.ru/vfs/credit/forms/101-20240101.rar"
    v_try = 0

    try:
        with urllib.request.urlopen(v_url) as resp:
            r = rarfile.RarFile(BytesIO(resp.read()))
            st.text ("Активы банков на " + v_txt_date + " г.")
    except urllib.error.URLError:
        st.text ("Данные на выбранную дату недоступны. Попытка вывести данные на 01.01.2024 г.")
        v_try = 1

    if v_try == 1:   
        try:
            with urllib.request.urlopen(v_url2) as resp:
                r = rarfile.RarFile(BytesIO(resp.read()))
                v_file_b = "122023N1.dbf"
                v_file_d = "122023B1.dbf"
                st.text ("Не найдены данные за выбранную дату")
                st.text ("Активы банков на 01.01.2024 г.")
                #st.text (v_url2)
        except urllib.error.URLError:
            st.text ("Данные на 01.01.2024 г. недоступны.")
            st.text ("К сожалению cbr.ru блокирует доступ к сайту при большом количестве запросов. Попробуйте позже")
            v_try = 2      

    if v_try != 2:
        r.extract(v_file_b)
        r.extract(v_file_d)
        
        # special class for correct parsing f101 from dbf. source: https://github.com/olemb/dbfread/issues/20#issuecomment-490289235
        class MyFieldParser(FieldParser):
            def parseN(self, field, data):
                data = data.strip().strip(b'*\x00')  # Had to strip out the other characters first before \x00, as per super function specs.
                return super(MyFieldParser, self).parseN(field, data)

            def parseD(self, field, data):
                data = data.strip(b'\x00')
                return super(MyFieldParser, self).parseD(field, data)
      
        # load content of a dbf file into a Pandas data frame
        dbf = DBF(v_file_d, parserclass=MyFieldParser, encoding='cp866')
        df = DataFrame(iter(dbf))
        df = df[df['A_P'] == '1']
        df = df[df['PLAN'] == 'А']
        df706 = df[df['NUM_SC'] == '706']
        df706['IITG'] = -1 * df706['IITG']
        df707 = df[df['NUM_SC'] == '707']
        df707['IITG'] = -1 * df707['IITG']
        merged_df = merge(df706, df707, on='REGN', how='left').fillna(0)
        merged_df['IITG'] = merged_df['IITG_x'] + merged_df['IITG_y']
        df71 = merged_df.drop(columns=merged_df.columns.difference(['REGN', 'NUM_SC', 'IITG']))

        df303 = df[df['NUM_SC'] == '303']
        df303['IITG'] = -1 * df303['IITG']
        merged_df = merge(df71, df303, on='REGN', how='left').fillna(0)
        merged_df['IITG'] = merged_df['IITG_x'] + merged_df['IITG_y']
        df7 = merged_df.drop(columns=merged_df.columns.difference(['REGN', 'NUM_SC', 'IITG']))

        df = df[df['NUM_SC'] == 'ITGAP'] #create frame with specific row - 'ITGAP' that contains the total value of assets
        df = df.drop(columns=df.columns.difference(['REGN', 'NUM_SC', 'IITG']))
        new_df = merge(df, df7, on='REGN', how='left').fillna(0)
        new_df['IITG'] = new_df['IITG_x'] + new_df['IITG_y']
        df = new_df
        # st.dataframe(data=df)    
        # df = df[df['REGN'] == 2312]
        # https://cbr.ru/banking_sector/credit/coinfo/f101/?regnum=2312&dt=2024-02-01

        # load content of a dbf file into a Pandas data frame
        dbf_names = DBF(v_file_b, parserclass=MyFieldParser, encoding='cp866')
        df_names = DataFrame(iter(dbf_names))
        df_names = df_names[['REGN','NAME_B']]
        df=df.merge(df_names, how = 'left')
        df=df.sort_values(by="IITG", ascending=[False]).head(v_num)
        df.insert(0, "RANK", range(1, 1 + len(df)))
        st.dataframe(data=df, column_order=("RANK","REGN","NAME_B","IITG"), column_config={"RANK":"№","REGN": "Рег.номер","NAME_B":"Наименование банка","IITG":"Активы (тыс.руб.)"}, hide_index=True)
        
    st.text("Источник данных: https://www.cbr.ru/banking_sector/otchetnost-kreditnykh-organizaciy/")
    st.text("Репозиторий: https://github.com/kapamob/streamlit-cbr-f123")


cbr_f123()

show_code(cbr_f123)

