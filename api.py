import os
import streamlit as st
import requests
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv('.env.local')

def send_stock_alerts(stock_name, company_name, user_phone_number):
    STOCK_ENDPOINT = "https://www.alphavantage.co/query"
    NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
    alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_KEY')
    news_api_key = os.getenv('NEWS_API_KEY')
    twilio_account_sid = os.getenv('TWILIO_SID')
    twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

    stock_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": stock_name,
        "apikey": alpha_vantage_api_key
    }
    response = requests.get(STOCK_ENDPOINT, params=stock_params)
    data = response.json()["Time Series (Daily)"]
    data_list = [value for (key, value) in data.items()]
    yesterday_data = data_list[0]
    yesterday_closing_price = yesterday_data["4. close"]
    day_before_yesterday_data = data_list[1]
    day_before_yesterday_closing_price = day_before_yesterday_data["4. close"]

    difference = float(yesterday_closing_price) - float(day_before_yesterday_closing_price)
    up_down = "🔺" if difference > 0 else "🔻"
    diff_percent = (difference / float(yesterday_closing_price)) * 100

    if abs(diff_percent) > 0:
        news_params = {
            "apiKey": news_api_key,
            "q": company_name,
            "searchIn": "title"
        }
        news_response = requests.get(NEWS_ENDPOINT, params=news_params)
        articles = news_response.json()["articles"][:3]

        formatted_articles = [f"{stock_name}: {up_down}{diff_percent:.2f}%\nHeadline: {article['title']}, \nBrief: {article['description']}" for article in articles]

        client = Client(twilio_account_sid, twilio_auth_token)
        for article in formatted_articles:
            message = client.messages.create(
                body=article,
                from_=twilio_phone_number,
                to=user_phone_number
            )
        return "Messages sent successfully!"
    else:
        return "No significant movement detected."

# Streamlit interface
st.title('Stock Alert System')

with st.form("stock_alert_form"):
    st_input_stock_name = st.text_input("Stock Symbol", value="QCOM")
    st_input_company_name = st.text_input("Company Name", value="QUALCOMM")
    st_input_phone_number = st.text_input("Your Phone Number", value="+917855947521")
    submitted = st.form_submit_button("Send Alert")

if submitted:
    result = send_stock_alerts(st_input_stock_name, st_input_company_name, st_input_phone_number)
    st.success(result)
