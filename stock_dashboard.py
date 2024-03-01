import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go

API_KEY = st.secrets["api"]["iex_key"]
API_BASE_URL = "https://cloud.iexapis.com/stable/"

def get_stock_data(symbol, time_range="5y"):
    params = {
        "token": API_KEY
    }

    response = requests.get(API_BASE_URL + f"stock/{symbol}/chart/{time_range}", params = params)
    data = response.json()

    if "error" in data:
        st.error(f"Error: {data['error']}")
        return None
    
    stock_data = pd.DataFrame(data)
    stock_data["date"] = pd.to_datetime(stock_data["date"])
    stock_data.set_index("date", inplace= True)
    stock_data = stock_data[["open", "high", "low", "close", "volume"]]
    stock_data.columns = ["Open", "High", "Low", "Close", "Volume"]
    return stock_data

def calculate_price_difference(stock_data):
    latest_price = stock_data.iloc[-1]["Close"]
    previous_year_price = stock_data.iloc[-252]["Close"] if len(stock_data) > 252 else stock_data.iloc[0]["Close"]
    price_difference = latest_price - previous_year_price
    percentage_difference = (price_difference / previous_year_price) * 100
    return price_difference, percentage_difference

def app():
    #--BOILERPLATE--#
    st.set_page_config(page_title="Stock Dashboard", layout="wide", page_icon="📈")
    hide_menu_style = "<style> footer {visibility: hidden;} </style>"
    st.markdown(hide_menu_style, unsafe_allow_html=True)

    st.title("📈 Dashboard Interativo de Ações")
    popular_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "PETR3", "FB", "VALE3", "ABEV3", "NVDA", "ITUB3"]
    symbol = st.sidebar.selectbox("Selecionar Ação: ", popular_symbols, index=2)

    if symbol:
        stock_data = get_stock_data(symbol)

        if stock_data is not None:
            price_difference, percentage_difference =  calculate_price_difference(stock_data)
            latest_close_price = stock_data.iloc[-1]["Close"]
            max_52_week_high = stock_data["High"].tail(252).max()
            min_52_week_low = stock_data["Low"].tail(252).min()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Preço Fechamento", f"${latest_close_price}")
            with col2:
                st.metric("Diferença de Preço Anual", f"${price_difference:.2f}", f"${percentage_difference:+.2f}%")
            with col3:
                st.metric("Alta Anual", f"$ {max_52_week_high:.2f}")
            with col4:
                st.metric("Baixa Anual", f"${min_52_week_low:.2f}")
            
            st.subheader("Gráfico de Velas")
            candlestick_chart = go.Figure(data=[go.Candlestick(x=stock_data.index, open=stock_data["Open"], high=stock_data["High"], low=stock_data["Low"], close=stock_data["Close"])])
            candlestick_chart.update_layout(title=f"{symbol} Gráfico de Velas", xaxis_rangeslider_visible = False)
            st.plotly_chart(candlestick_chart, use_container_width=True)

            st.subheader("Sumário")
            st.dataframe(stock_data.tail())

            st.download_button("Baixe o Resumo dos Dados das Ações", stock_data.to_csv, file_name=f"{symbol}_dados_acoes", mime="text/csv")

if __name__ == "__main__":
    app()

