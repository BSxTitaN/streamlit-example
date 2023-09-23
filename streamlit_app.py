from collections import namedtuple
import numpy as np
from tensorflow import keras
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import datetime

"""
# Welcome to JPN-SEN-Analysis

Upload the required `JPN-Data.csv` file to get started 
"""

model = keras.models.load_model('my_model.keras')
today = datetime.datetime.now()
next_year = today.year + 1
jan_1 = datetime.date(next_year, 1, 1)
dec_31 = datetime.date(next_year, 12, 31)

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
date_range_option = st.selectbox(
    "Select Date Range",
    ["1 hour", "1 day", "1 week", "1 month", "Custom"]
)

if date_range_option == "Custom":
    st.subheader("Custom Date Range Picker")
    d = st.date_input(
        "Select your vacation for next year",
        (jan_1, datetime.date(next_year, 1, 7)),
        jan_1,
        dec_31,
        format="MM.DD.YYYY",
    )
    d

tweet_station = st.selectbox(
    "Select Twitter Handle",
    ["Toyota Motorcorp", "Yo Sushi Restaurant", "Nobu Restaurant", "7-11 Store"]
)

st.title("Analysis Zone")

if uploaded_file is not None:
    # Read CSV file
    df = pd.read_csv(uploaded_file)

    # Check if the CSV contains a "Japanese" column
    if "Japanese" not in df.columns:
        st.error("The CSV file must contain a 'Japanese' column.")
    else:
        # Perform sentiment analysis
        x = df['Japanese']

        # Preprocess the text (similar to what you did during training)
        max_len = 1000
        tok = Tokenizer(num_words=1500)
        tok.fit_on_texts(x)
        sequences = tok.texts_to_sequences(x)
        sequences_matrix = sequence.pad_sequences(
            sequences, maxlen=max_len)

        # Make predictions using the model
        predictions = model.predict(sequences_matrix)
        sentiment_labels = np.argmax(predictions, axis=1).tolist()

        # Calculate sentiment statistics
        total_samples = len(sentiment_labels)
        negative_count = sentiment_labels.count(0)
        positive_count = sentiment_labels.count(1)
        neutral_count = sentiment_labels.count(2)

        # Calculate percentages
        negative_percentage = (negative_count / total_samples) * 100
        positive_percentage = (positive_count / total_samples) * 100
        neutral_percentage = (neutral_count / total_samples) * 100

        # Display sentiment statistics as cards
        st.subheader("Sentiment Analysis Results")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Negative", negative_count)
            st.metric("Negative %", negative_percentage)

        with col2:
            st.metric("Positive", positive_count)
            st.metric("Positive %", positive_percentage)

        with col3:
            st.metric("Neutral", neutral_count)
            st.metric("Neutral %", neutral_percentage)

        # Create Pie Chart 1 for sentiment distribution
        sentiment_counts = pd.Series(sentiment_labels).value_counts()
        sentiment_colors = px.colors.qualitative.Plotly
        fig_pie_1 = go.Figure(data=[go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            textinfo='percent+value+label',
            marker_colors=sentiment_colors,
            textposition='auto',
            hole=0.3
        )])

        fig_pie_1.update_layout(
            title_text='Sentiment Distribution',
            template='plotly_white'
        )

        # Create Pie Chart 2 for sentiment distribution
        volume_data = {
            'Sentiment': ['Negative', 'Positive', 'Neutral'],
            'Volume': [negative_count, positive_count, neutral_count]
        }
        fig_bar = go.Figure(data=[go.Bar(
            x=volume_data['Sentiment'],
            y=volume_data['Volume'],
            text=volume_data['Volume'],
            textposition='outside',
            marker_color=sentiment_colors[:3]
        )])

        fig_bar.update_layout(
            title_text='Sentiment Volume Comparison',
            template='plotly_white',
            xaxis_title='Sentiment',
            yaxis_title='Volume'
        )

        # Streamlit layout
        st.subheader("Sentiment Analysis Results")
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(fig_pie_1, use_container_width=True)  # Display Pie Chart 1

        with col2:
            st.plotly_chart(fig_bar, use_container_width=True)  # Display Pie Chart 2

        # Display top 5 tweets with random data (replace with actual data)
        st.subheader("Top 5 Tweets")
        tweets_data = [['56431', '雅子様のセンスですかね', 'Positive'],
               ['879398', '私ら庶民の母親にはできないスカート丈(お嬢様かお姫様丈)', 'Netural'],
               ['8831573', 'やっぱり皇太子(天皇)より皇太子妃(皇后)のほうがデカいって見栄え最悪だな　ノミの夫婦', 'Negative'],
               ['76347', '食べ物はそれほど悪くありませんでした', 'Positive'],
               ['387863', '浪川大輔さんから頂いた！！', 'Netural']]

        # Convert the list of lists to a DataFrame
        selected_tab = st.tabs(["Happy", "Sad", "Neutral"])
        if selected_tab == "Happy":
            filtered_tweets = df[df['Senti'] == "Positive"]
        elif selected_tab == "Sad":
            filtered_tweets = df[df['Senti'] == "Negative"]
        else:
            filtered_tweets = df[df['Senti'] == "Neutral"]

        # Remove the "Unnamed: 0" and "Unnamed: 0.1" columns
        if "Unnamed: 0" in filtered_tweets.columns:
            filtered_tweets = filtered_tweets.drop(columns=["Unnamed: 0", "Unnamed: 0.1"])

        # Convert the list of lists to a DataFrame
        st.dataframe(filtered_tweets, height=150)

else:
    st.text("Upload the file to display result!")

# # Footer
# st.footer("Made by Harsh in Streamlit")