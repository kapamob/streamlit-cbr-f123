import os
import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import sqlalchemy as sql
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import plotly.graph_objects as go

LOGGER = get_logger(__name__)

engine = sql.create_engine("mysql+mysqlconnector://"+st.secrets.K_USER+":"+st.secrets.K_MOTDEPASS+"@"+st.secrets.K_IP+":"+st.secrets.K_PORT+"/"+st.secrets.K_DB)

def cbr_f123_charts():
    st.set_page_config(page_title="Капитал банков (график)", page_icon="📊")
    st.sidebar.header("Капитал банков (график)")

    st.write("# Капитал банков по ф.123 (график)")
    st.write("Динамика значений капитала банков с 2011 года в абсолютном (верхний график) и относительном (сумма положительных значений капиталов на дату = 100%) выражении. Для просмотра на полный экран используйте элементы управления в правом верхнем углу графиков.")

    fig1 = render_chart1(engine=engine)
    fig1.update_layout(barmode="relative", margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgb(0, 0, 0)", autosize=False,
    width=1525,
    height=685,)
    st.plotly_chart(fig1, use_container_width=True)
    fig2 = render_chart2(engine=engine)
    fig2.update_layout(barmode="relative", margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgb(0, 0, 0)", autosize=False,
    width=1525,
    height=685,)
    st.plotly_chart(fig2, use_container_width=True)

def req(s, engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.execute(text(f"{s}"))
    df = pd.DataFrame(result)
    return df

def render_chart1(engine, year='2024'):
    s = f"""SELECT capital_money.*, banks.bank_name 
              FROM capital_money 
              LEFT JOIN banks ON banks.regn=capital_money.regn 
             WHERE year(capital_money.dt) > 2010 
               and capital_money.value > 1 
               and month(capital_money.dt) in (1,4,7,10)
             ORDER BY dt, value DESC;"""
    df = req(s, engine)
    df['dt'] = pd.to_datetime(df['dt'])
    date_list = df["dt"].unique()
    fig = go.Figure()
    final_df = pd.DataFrame()
    for cur_date in date_list[::-1]:
        tmp_df = df.loc[df['dt'] == cur_date, :]
        tmp_df.sort_values(by=['value'], ascending=True, inplace=False, na_position='last', kind='quicksort',
                           ignore_index=False)
        r = tmp_df.head(20)
        final_df = pd.concat([final_df, r], ignore_index=True)
        if len(tmp_df) > 30:
            r = tmp_df.iloc[20:30]
            r = pd.DataFrame(
                [{"dt": cur_date, "kod": "000", "regn": "-1", "value": sum(r.value), "bank_name": "top 21-30"}])
            final_df = pd.concat([final_df, r], ignore_index=True)
        if len(tmp_df) > 50:
            r = tmp_df.iloc[30:50]
            r = pd.DataFrame(
                [{"dt": cur_date, "kod": "000", "regn": "-1", "value": sum(r.value), "bank_name": "top 31-50"}])
            final_df = pd.concat([final_df, r], ignore_index=True)
        if len(tmp_df) > 100:
            r = tmp_df.iloc[50:100]
            r = pd.DataFrame(
                [{"dt": cur_date, "kod": "000", "regn": "-1", "value": sum(r.value), "bank_name": "top 51-100"}])
            final_df = pd.concat([final_df, r], ignore_index=True)
        if len(tmp_df) > 100:
            r = tmp_df.iloc[100:]
            r = pd.DataFrame(
                [{"dt": cur_date, "kod": "000", "regn": "-1", "value": sum(r.value), "bank_name": "top 100 и больше"}])
            final_df = pd.concat([final_df, r], ignore_index=True)

    names = list(final_df["bank_name"].unique())
    names.remove('top 21-30')
    names.remove('top 31-50')
    names.remove('top 51-100')
    names.remove('top 100 и больше')
    names.append('top 21-30')
    names.append('top 31-50')
    names.append('top 51-100')
    names.append('top 100 и больше')
    color = get_colors(names)
    for name in names:
        filtered_df = final_df[final_df['bank_name'] == name]
        filtered_df['value'] = filtered_df['value'].apply(lambda x: x /1000000)
        fig.add_trace(go.Bar(
            y=filtered_df["dt"],
            x=filtered_df["value"],
            name=name,
            orientation='h',
            hoverinfo = 'x+name',
            hovertemplate="%{x:.1f} млрд",
            marker=dict(
                color=color[name],
                # line=dict(color='rgba(246, 78, 139, 1.0)', width=3)
            )
        ))

    fig.update_layout(barmode='relative', margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgb(175, 225, 255)", autosize=False,
        width=1525,
        height=685,
    )

    fig.update_yaxes(
        tickformat="%Y", # Формат даты для меток
        dtick='M12'
    )

    return fig

def render_chart2(engine, year='2024'):
    s = f"""SELECT capital_money.*, banks.bank_name 
 FROM capital_money 
 LEFT JOIN banks ON banks.regn=capital_money.regn 
WHERE year(capital_money.dt) > 2010 
  and capital_money.value > 1 
  and month(capital_money.dt) in (1,4,7,10)
    ORDER BY dt, value DESC;"""
    df = req(s, engine)
    df['dt'] = pd.to_datetime(df['dt'])
    date_list = df["dt"].unique()
    df.sort_values(by=['value'], ascending=True, inplace=False, na_position='last', kind='quicksort',
                       ignore_index=False)
    fig = go.Figure()
    final_df = pd.DataFrame()
    for cur_date in date_list[::-1]:
        tmp_df = df.loc[df['dt'] == cur_date, :]
        tmp_df.sort_values(by=['value'], ascending=True, inplace=False, na_position='last', kind='quicksort',
                           ignore_index=False)
        r = tmp_df.head(20)
        tmp = tmp_df
        tmp_df = pd.DataFrame()
        tmp_df = pd.concat([tmp_df, r], ignore_index=True)
        if len(tmp) > 30 or 1:
            r = tmp.iloc[20:30]
            r = pd.DataFrame(
                [{"dt": cur_date, "kod": "000", "regn": "-1", "value": sum(r.value), "bank_name": "top 21-30"}])
            tmp_df = pd.concat([tmp_df, r], ignore_index=True)
        if len(tmp) > 50 or 1:
            r = tmp.iloc[30:50]
            r = pd.DataFrame(
                [{"dt": cur_date, "kod": "000", "regn": "-1", "value": sum(r.value), "bank_name": "top 31-50"}])
            tmp_df = pd.concat([tmp_df, r], ignore_index=True)
        if len(tmp) > 100 or 1:
            r = tmp.iloc[50:100]
            r = pd.DataFrame(
                [{"dt": cur_date, "kod": "000", "regn": "-1", "value": sum(r.value), "bank_name": "top 51-100"}])
            tmp_df = pd.concat([tmp_df, r], ignore_index=True)
        if len(tmp) > 100 or 1:
            r = tmp.iloc[100:]
            r = pd.DataFrame(
                [{"dt": cur_date, "kod": "000", "regn": "-1", "value": sum(r.value), "bank_name": "top 100 и больше"}])
            tmp_df = pd.concat([tmp_df, r], ignore_index=True)
        total_sum = tmp_df['value'].sum()
        tmp_df['percent'] = (tmp_df['value'] / total_sum) * 100

        final_df = pd.concat([tmp_df, final_df], ignore_index=True)
    #final_df.sort_values(by=['value'], ascending=True, inplace=False, na_position='last', kind='quicksort',
    #                       ignore_index=False)
    final_df.sort_values(by=['dt', 'value'], ascending=False, inplace=True, na_position='last', kind='quicksort',
                           ignore_index=False)
    print(final_df.info)
    names = list(final_df["bank_name"].unique())
    names.remove('top 21-30')
    names.remove('top 31-50')
    names.remove('top 51-100')
    names.remove('top 100 и больше')
    names.append('top 21-30')
    names.append('top 31-50')
    names.append('top 51-100')
    names.append('top 100 и больше')
    color = get_colors(names)
    for name in names:
        filtered_df = final_df[final_df['bank_name'] == name]
        filtered_df['value'] = filtered_df['value'].apply(lambda x: x /1000000)
        fig.add_trace(go.Bar(
            y=filtered_df["dt"],
            x=filtered_df["percent"],
            name=name,
            orientation='h',
            hoverinfo = 'x+name',
            hovertemplate="%{x:.1f} млрд",
            marker=dict(
                color=color[name],
                # line=dict(color='rgba(246, 78, 139, 1.0)', width=3)
            )
        ))

    fig.update_layout(barmode='relative', margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgb(175, 225, 255)", autosize=False,
        width=1525,
        height=685, hoverlabel_font_color='rgb(0, 0, 0)',
    )
    
    fig.update_yaxes(
        tickformat="%Y", # Формат даты для меток
        dtick='M12'
    )
   
    return fig



def get_colors(lst):
    m = ['RGB(255, 255, 0)', 'RGB(0, 0, 255)', 'RGB(255, 0, 0)', 'RGB(255, 69, 0)', 'RGB(255, 255, 100)',
         'RGB(0, 0, 139)', 'RGB(255, 165, 0)', 'RGB(0, 0, 205)', 'RGB(220, 20, 60)', 'RGB(255, 140, 0)',
         'RGB(70, 130, 180)', 'RGB(205, 92, 92)', 'RGB(255, 215, 0)', 'RGB(30, 144, 255)', 'RGB(128, 0, 0)',
         'RGB(218, 165, 32)', 'RGB(65, 105, 225)', 'RGB(255, 69, 0)', 'RGB(0, 191, 255)', 'RGB(165, 42, 42)',
         'RGB(255, 140, 0)', 'RGB(25, 25, 112)', 'RGB(139, 0, 0)', 'RGB(255, 99, 71)', 'RGB(0, 206, 209)',
         'RGB(244, 164, 96)', 'RGB(70, 130, 180)', 'RGB(220, 20, 60)', 'RGB(255, 215, 0)', 'RGB(75, 0, 130)',
         'RGB(205, 92, 92)', 'RGB(255, 99, 71)', 'RGB(46, 139, 87)', 'RGB(128, 0, 0)', 'RGB(160, 82, 45)',
         'RGB(70, 130, 180)', 'RGB(218, 165, 32)', 'RGB(0, 191, 255)', 'RGB(255, 99, 71)', 'RGB(65, 105, 225)',
         'RGB(0, 0, 255)', 'RGB(255, 0, 0)', 'RGB(255, 69, 0)', 'RGB(255, 255, 100)',
         'RGB(0, 0, 139)', 'RGB(255, 165, 0)', 'RGB(0, 0, 205)', 'RGB(220, 20, 60)', 'RGB(255, 140, 0)',
         'RGB(70, 130, 180)', 'RGB(205, 92, 92)', 'RGB(255, 215, 0)', 'RGB(30, 144, 255)', 'RGB(128, 0, 0)',
         'RGB(218, 165, 32)', 'RGB(65, 105, 225)', 'RGB(255, 69, 0)', 'RGB(0, 191, 255)', 'RGB(165, 42, 42)',
         'RGB(255, 140, 0)', 'RGB(25, 25, 112)', 'RGB(139, 0, 0)', 'RGB(255, 99, 71)', 'RGB(0, 206, 209)',
         'RGB(244, 164, 96)', 'RGB(70, 130, 180)', 'RGB(220, 20, 60)', 'RGB(255, 215, 0)', 'RGB(75, 0, 130)',
         'RGB(205, 92, 92)', 'RGB(255, 99, 71)', 'RGB(46, 139, 87)', 'RGB(128, 0, 0)', 'RGB(160, 82, 45)',
         'RGB(70, 130, 180)', 'RGB(218, 165, 32)', 'RGB(0, 191, 255)', 'RGB(255, 99, 71)', 'RGB(65, 105, 225)']
    d = {'ПАО Сбербанк': 'rgb(51, 153, 51)', 'Банк ВТБ (ПАО)': 'rgb(0, 153, 255)',
         'ПАО Банк ФК Открытие': 'rgb(0, 153, 255)', 'ВТБ 24 (ПАО)': 'rgb(0, 153, 255)',
         'Банк ГПБ (АО)': 'rgb(0, 51, 204)', 'АО АЛЬФА-БАНК': 'rgb(255, 0, 0)', 'НКО НКЦ (АО)': 'rgb(102, 102, 153)',
         'ПАО МОСКОВСКИЙ КРЕДИТНЫЙ БАНК': 'rgb(153, 0, 51)', 'АО Россельхозбанк': 'rgb(0, 102, 0)',
         'ПАО Совкомбанк': 'rgb(255, 102, 153)', 'АО Банк ДОМ.РФ': 'rgb(153, 204, 0)',
         'АО Тинькофф Банк': 'rgb(255, 255, 0)', 'ПАО РОСБАНК': 'rgb(0, 51, 102)',
         'АО Райффайзенбанк': 'rgb(255, 255, 102)', 'НКО АО НРД': 'rgb(102, 102, 153)',
         'АО АБ РОССИЯ': 'rgb(0, 153, 204)', 'АО ЮниКредит Банк': 'rgb(227, 36, 0)',
         'ПАО Банк Санкт-Петербург': 'rgb(255, 0, 102)', 'АО АКБ НОВИКОМБАНК': 'rgb(153, 0, 255)',
         'ПАО АК БАРС БАНК': 'rgb(0, 204, 102)', 'ПАО БАНК УРАЛСИБ': 'rgb(102, 0, 204)',
         'АО КБ Ситибанк': 'rgb(0, 153, 255)', 'ПАО Промсвязьбанк': 'rgb(255, 102, 0)'}
    j = 4
    for i in lst:
        if not i in d.keys():
            d[i] = m[j]
            j += 1
    return d


cbr_f123_charts()
