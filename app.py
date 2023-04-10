import streamlit as st  
import openai
from dotenv import load_dotenv
import os 
import requests
import json
load_dotenv()

weather_api_key = os.getenv("WEATHER_API")

def add_openai_api_key():
  openai.api_key = st.session_state.openai_api_key


def extract_city():
    system_message = {"role" : "system", "content" : "You are a helpful text parser."}
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[system_message, {
        "role": "user",
        "content" : 'Extract the city from the following message in the following format: "{"city": "" } :' +  st.session_state.message}])
    
    city_str = completion.choices[0].message.content
    city = json.loads(city_str)["city"]

    return city
  
def extract_weather_data_json(city):
  url = "http://api.weatherapi.com/v1/current.json?key=" + weather_api_key +  "&q=" + city + "&aqi=no"
   
  response = requests.get(url)
  data = response.json()

  return data

def get_weather_data(json_data):
  system_message = {"role": "system", "content": "You are a helpful json interpreter"}
  completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[system_message, {
    "role": "user",
    "content": 'Get current weather insights from the following data : ' + json_data}])
  weather_insights = completion.choices[0].message.content
  return weather_insights

def on_message_change():
    if st.session_state.openai_api_key == "":
      st.error("Please add your Openai API Key", icon="🚨")
    else:
      try:
        st.session_state.history.append({"role": "user" , "content": st.session_state.message})
        city = extract_city()
        json_data = extract_weather_data_json(city)
        weather_insights = get_weather_data(json.dumps(json_data))
        st.session_state.history.append({"role" : "assistant", "content" : weather_insights})
        st.session_state.message = ""
      except openai.error.AuthenticationError:
        st.error("Your API key or token is invalid, expired, or revoked. Check again and update your API key", icon="🚨")


def main():
  st.set_page_config(
    page_title="ChatGPT Weather Anchor",
    page_icon="🍃",
    menu_items={
        'Get Help': 'https://platform.openai.com/account/api-keys',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': """#### Streamlit weather app powered by ChatGPT. *Ask ChatGPT how is the weather today in your location.*
                  Author: https://bento.me/catalina"""
    }
  )    
  st.title("Get weather insights with ChatGPT")
  system_message = {"role" : "system", "content" : "You are a weather anchor."}

  if "history" not in st.session_state:
      st.session_state.history = [system_message]

  if "openai_api_key" not in st.session_state:
      st.session_state.openai_api_key = ""

  for message in st.session_state.history:
      if message["role"] == "user":
        st.write('<p style="color:limegreen;text-align:right;">' + "User: " + message["content"] + '</p>', unsafe_allow_html=True)
      elif message["role"] == "assistant":
        st.write("ChatGPT: " + message["content"])
      else:
        st.write("System: " + message["content"])
         

  st.text_input(label="Message", key="message", placeholder = 'Ask ChatGPT how is the weather today in your location.', on_change=on_message_change, label_visibility="hidden")
  st.text_input(label="openai_api_key", key = "openai_api_key", type = "password", placeholder = 'Add your Openai API Key here', on_change=add_openai_api_key, label_visibility="hidden")

main()
