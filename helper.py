from urlextract import URLExtract
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()


def most_talkative_user(df):
    most_talkative = df['user'].value_counts().idxmax()
    percent_messages = (df[df['user'] == most_talkative].shape[0] / df.shape[0]) * 100
    return most_talkative, percent_messages


def influencer_user(df):
    influencer = df[df['message'] == '<Media omitted>\n']['user'].value_counts().idxmax()
    percent_media_messages = (df[(df['user'] == influencer) & (df['message'] == '<Media omitted>\n')].shape[0] /
                              df.shape[0]) * 100
    return influencer, percent_media_messages


def long_winded_user(df):
    long_winded_user = df[df['message'].apply(len) > 110]['user'].value_counts().idxmax()
    percent_long_winded = (df[(df['user'] == long_winded_user) & (df['message'].apply(len) > 110)].shape[0] / df.shape[
        0]) * 100
    return long_winded_user, percent_long_winded


import emoji

def emoji_lover_user(df):
    emoji_counts = []

    # Iterate over each user
    for user in df['user'].unique():
        if user != 'group_notification':
            user_df = df[df['user'] == user]

            # Count emojis in user's messages
            total_messages = user_df.shape[0]
            emoji_messages = user_df['message'].apply(lambda x: any(char in emoji.UNICODE_EMOJI['en'] for char in x)).sum()

            # Calculate percentage of messages with emojis
            percent_emoji_messages = (emoji_messages / total_messages) * 100

            emoji_counts.append((user, percent_emoji_messages))

    # Find the user with the highest percentage of messages containing emojis
    emoji_lover_user, percent_emoji_lover = max(emoji_counts, key=lambda x: x[1])

    return emoji_lover_user, percent_emoji_lover



def early_bird_user(df):
    early_bird_user = df[(df['hour'] >= 5) & (df['hour'] <= 10)]['user'].value_counts().idxmax()
    percent_early_bird = (df[(df['user'] == early_bird_user) & (df['hour'] >= 5) & (df['hour'] <= 10)].shape[0] /
                          df.shape[0]) * 100
    return early_bird_user, percent_early_bird


def night_owl_user(df):
    night_owl_user = df[((df['hour'] >= 23) | (df['hour'] <= 3))]['user'].value_counts().idxmax()
    percent_night_owl = (df[(df['user'] == night_owl_user) & ((df['hour'] >= 23) | (df['hour'] <= 3))].shape[0] /
                         df.shape[0]) * 100
    return night_owl_user, percent_night_owl


def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x, df


def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df


def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df


def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline


def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap

