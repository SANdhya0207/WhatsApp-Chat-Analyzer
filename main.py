import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from helper import most_talkative_user, influencer_user, long_winded_user, emoji_lover_user, early_bird_user, night_owl_user
import emoji

analyzer = SentimentIntensityAnalyzer()
st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    # st.text(data) -> Display the whole chat
    df = preprocessor.preprocess(data)

    # st.dataframe(df) -> Show data in columns as done in jupyter

    # Fetching different users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        if selected_user == "Overall":
            # Most Talkative User
            most_talkative, percent_talkative = most_talkative_user(df)
            st.title("🗣️ Most Talkative User 🗣️")
            st.write(
                f"The most talkative user is {most_talkative} with {percent_talkative:.2f}% of the total messages.")

            # Influencer User
            influencer, percent_influencer = influencer_user(df)
            st.title("📸 Influencer User 📸")
            st.write(
                f"The influencer user who sends the highest number of media messages is {influencer} with {percent_influencer:.2f}% of the total media messages.")

            # Arrange "Most Talkative User" and "Influencer User" into two columns
            col1, col2 = st.columns(2)

            with col1:
                # Long Winded User
                long_winded, percent_long_winded = long_winded_user(df)
                st.title("📜 Long Winded User 📜")
                st.write(
                    f"The long-winded user is {long_winded} with {percent_long_winded:.2f}% of the total messages longer than 110 characters.")

                # Early Bird User
                early_bird, percent_early_bird = early_bird_user(df)
                st.title("🌅 Early Bird User 🌅")
                st.write(
                    f"The early bird user is {early_bird} with {percent_early_bird:.2f}% of the total messages sent between 5 AM and 10 AM.")

            with col2:
                # Emoji Lover User
                emoji_lover, percent_emoji_lover = emoji_lover_user(df)
                st.title("😍 Emoji Lover User 😍")
                st.write(
                    f"The emoji lover user is {emoji_lover} with {percent_emoji_lover:.2f}% of the total messages containing emojis.")

                # Night Owl User
                night_owl, percent_night_owl = night_owl_user(df)
                st.title("🦉 Night Owl User 🦉")
                st.write(
                    f"The night owl user is {night_owl} with {percent_night_owl:.2f}% of the total messages sent between 11 PM and 3 AM.")

        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig,ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'],color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1,col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x,new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values,color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # most common words
        most_common_df = helper.most_common_words(selected_user, df)

        fig,ax = plt.subplots()

        ax.barh(most_common_df[0],most_common_df[1])
        plt.xticks(rotation='vertical')

        st.title('Most common words')
        st.pyplot(fig)

        # emoji analysis
        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")

        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig,ax = plt.subplots()
            ax.pie(emoji_df[1].head(),labels=emoji_df[0].head(), autopct="%0.2f")
            st.pyplot(fig)

        # Sentiment analysis
        st.title("Sentiment Analysis")

        # Create a column for sentiment analysis
        df['sentiment'] = df['message'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

        # Display sentiment distribution
        st.header("Sentiment Distribution")
        fig, ax = plt.subplots()
        sns.histplot(df['sentiment'], bins=30, kde=True, color='blue', ax=ax)
        st.pyplot(fig)

        # Display average sentiment
        st.header("Average Sentiment")
        average_sentiment = df['sentiment'].mean()
        st.write(f"The average sentiment is: {average_sentiment:.2f}")
else:
    st.write("# In order to use our analyser you need to export your WhatsApp Chat to a text file")
    st.write("1. Open the individual or group chat.")
    st.write("2. Tap more options (:) -> More -> Export Chat")
    st.write("3. Choose to export without Media")
    st.write(" Tap on the [link](https://faq.whatsapp.com/1180414079177245/?cms_platform=android) for more details.")

