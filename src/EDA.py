# import seaborn as sns
# import matplotlib_inline.backend_inline
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from plotly.subplots import make_subplots
# import plotly.graph_objects as go
# from skimage import io
import streamlit as st
from processing import *

def BoW_eda(df, n=30, text_column='caption', drop=['<number>'], context='paper', title_suffix=None,
    filename=None, path=r'C:\Users\silvh\OneDrive\data science job search\content'):
    sns.reset_defaults()    
    # %matplotlib inline
    # matplotlib_inline.backend_inline.set_matplotlib_formats('retina')
    plt.rcParams['savefig.dpi'] = 300
    
    # sns.set_theme(context=context, style='ticks')
    df = df.drop(columns=drop)
    top_n = df.sum().sort_values(ascending=False).head(n).sort_values()
    # ax = sns.barplot(df[top_n.index.tolist()], estimator='sum',errorbar=None) # this works but gives deprecated warning
    fig, ax = plt.subplots()
    ax.barh(top_n.index, top_n)
    ax.set_yticks(top_n.index) # This line suppresses the warning "UserWarning: FixedFormatter should only be used together with FixedLocator"
    title = f'Top {n} words in Instagram posts'
    if title_suffix:
        title = f'{title}: {title_suffix}'
    ax.set(xlabel='Count', ylabel='Word', title=title)
    ax.axis('tight')
    if filename:
        try:
            path = f'{path}/'.replace('\\','/')
            fig.savefig(path+filename, bbox_inches='tight')
            print('Saved: ', path+filename)
        except:
            print('Unable to save outputs')
    print('Time completed:', datetime.now())

    return top_n

@st.cache_data
def plot_images(df, n=6, top=True, max_columns=5, streamlit=False, timezone='Canada/Pacific'):
    """
    Plot the images/video thumbnails of either the top or 
    worst performing instagram media (posts, reels, carousels).
    The following data is shown for each resulting media item:
        - Image/video thumbnail
        - Time stamp of the post in the provided time zone or in UTC time.
        - Number of likes and number of comments.

    Parameters:
        - df: DataFrame with the processed data.
        - n (int): Number of images to show.
        - top (bool): If True, plot images with the highest number of likes in 
            descending order. If False, plot images with the highest number of likes in
            ascending order. sort_by = ['like_count', 'comments_count', 'timestamp']
        - streamlit (bool): Whether or not the app runs on Streamlit. If False, then
            it is run on local machine.
        - timezone (str): Timezone parameter for the `.astimezone()` method.
            e.g. 'Australia/Sydney', 'Canada/Pacific'
    Returns:
        - DataFrame containing the data of the posts in the figure.
        - fig: Plotly figure object.
    """
    ncols = n if n<max_columns else max_columns
    nrows = (n + ncols - 1) // ncols
    sort_by = ['like_count', 'comments_count', 'timestamp']
    posts = df.sort_values(by=sort_by, ascending=False if top else True).head(n).copy()
    posts['thumbnail_url'].fillna(posts['media_url'], inplace=True)
    if timezone:
        print('Time zone:', timezone)
        converted_timestamp = [timestamp.astimezone(timezone) for timestamp in pd.to_datetime(posts['timestamp'])]
        titles = tuple(timestamp.strftime('%Y-%m-%d at %H:%M') for timestamp in converted_timestamp)
    else:
        titles = tuple(posts['timestamp'].dt.strftime('%Y-%m-%d at %H:%M').values.tolist())
    fig = make_subplots(rows=nrows, cols=ncols, subplot_titles=titles)
    for index, (n_likes, n_comments, url) in enumerate(zip(
            posts['like_count'], posts['comments_count'], posts['thumbnail_url'])
        ):
        fig.add_layout_image(
            x=0, y=0,
            xanchor='center', yanchor='middle',
            sizex=1, sizey=1,
            row=index // ncols + 1,
            col=index % ncols + 1,
            xref="x",
            yref="y",
            opacity=1.0,
            source=url
        )
        fig.add_annotation(
            xref="x domain",
            yref="y domain",
            x=0.5,
            y=-.10,
            text=f'{n_likes} likes, {n_comments} comments',
            axref="x domain",
            ayref="y",
            ax=0.5,
            ay=2,
            arrowhead=2,
            row=index // ncols + 1,
            col=index % ncols + 1,
        )
    fig.update_xaxes(range=[-0.5,0.5], showticklabels=False)
    fig.update_yaxes(range=[-0.5,0.5], showticklabels=False)
    fig.update_layout(plot_bgcolor="white")
    if streamlit:
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig.show()
    return posts.reset_index(drop=True), fig

def plot_images_tfidf(input_df, count_vector,
        n=6, top=True, max_columns=5, streamlit=False, timezone='Canada/Pacific'):
    """
    Plot the images/video thumbnails of either the top or 
    worst performing instagram media (posts, reels, carousels).
    The following data is shown for each resulting media item:
        - Image/video thumbnail
        - Time stamp of the post in the provided time zone or in UTC time.
        - Number of likes and number of comments.
        - 5 words with the highest Tf-idf scores.

    Parameters:
        - df: DataFrame with the processed data.
        - count_vector: DataFrame with the count vectors.
        - n (int): Number of images to show.
        - top (bool): If True, plot images with the highest number of likes in 
            descending order. If False, plot images with the highest number of likes in
            ascending order. sort_by = ['like_count', 'comments_count', 'timestamp']
        - streamlit (bool): Whether or not the app runs on Streamlit. If False, then
            it is run on local machine.
        - timezone (str): Timezone parameter for the `.astimezone()` method.
            e.g. 'Australia/Sydney', 'Canada/Pacific'
    Returns:
        - DataFrame containing the data of the posts in the figure.
        - fig: Plotly figure object.
    """
    tfidf = tfidf_transform(count_vector)
    ncols = n if n<max_columns else max_columns
    nrows = (n + ncols - 1) // ncols
    sort_by = ['like_count', 'comments_count', 'timestamp']
    df = pd.concat([input_df, tfidf], axis=1)
    posts = df.sort_values(by=sort_by, ascending=False if top else True).head(n).copy()
    posts['thumbnail_url'].fillna(posts['media_url'], inplace=True)
    # posts['caption'] = posts['caption'].fillna('haha')
    if timezone:
        print('Time zone:', timezone)
        converted_timestamp = [timestamp.astimezone(timezone) for timestamp in pd.to_datetime(posts['timestamp'])]
        titles = tuple(timestamp.strftime('%Y-%m-%d at %H:%M') for timestamp in converted_timestamp)
    else:
        titles = tuple(posts['timestamp'].dt.strftime('%Y-%m-%d at %H:%M').values.tolist())
    fig = make_subplots(
        rows=nrows, cols=ncols, 
        vertical_spacing=0.55/nrows
        )
    for index, (i, n_likes, n_comments, url, title) in enumerate(zip(posts.index,
            posts['like_count'], posts['comments_count'], posts['thumbnail_url'],
            titles)
        ):
        highest_tfidf = [word for word, value in tfidf.loc[i].sort_values(
            ascending=False).head(5).items() if value > 0]
        fig.add_layout_image(
            x=0, y=0,
            xanchor='center', yanchor='middle',
            sizex=1, sizey=1,
            row=index // ncols + 1,
            col=index % ncols + 1,
            xref="x",
            yref="y",
            opacity=1.0,
            source=url
        )
        annotation_y_position = -0.075
        fig.add_annotation(
            xref="x domain",
            yref="y domain",
            x=0.5,
            y=1.1,
            text=title,
            axref="x domain",
            ayref="y",
            ax=0.5,
            ay=2,
            arrowhead=2,
            row=index // ncols + 1,
            col=index % ncols + 1,
        )
        fig.add_annotation(
            xref="x domain",
            yref="y domain",
            x=0.5,
            y=annotation_y_position,
            text=f'{n_likes} likes, {n_comments} comments',
            axref="x domain",
            ayref="y",
            ax=0.5,
            ay=2,
            arrowhead=2,
            row=index // ncols + 1,
            col=index % ncols + 1,
        )
        annotation_y_position -= 0.1
        fig.add_annotation(
            xref="x domain",
            yref="y domain",
            x=0.5,
            y=annotation_y_position,
            text=f'Most unique words:',
            axref="x domain",
            ayref="y",
            ax=0.5,
            ay=2,
            arrowhead=2,
            row=index // ncols + 1,
            col=index % ncols + 1,
        )
        for word in highest_tfidf:
            annotation_y_position -= .075
            fig.add_annotation(
                xref="x domain",
                yref="y domain",
                x=0.5,
                y=annotation_y_position,
                text=word,
                axref="x domain",
                ayref="y",
                ax=0.5,
                ay=2,
                arrowhead=2,
                row=index // ncols + 1,
                col=index % ncols + 1,
                # hovertext=caption,
            )
    fig.update_xaxes(range=[-0.5,0.5], showticklabels=False)
    fig.update_yaxes(range=[-0.5,0.5], showticklabels=False)
    fig.update_layout(
        title_text='Posts with highest number of likes' if top==True else 'Posts with fewest number of likes',
        title_xanchor='center', title_x=0.5,
        plot_bgcolor="white", 
        height = 120 + nrows * 300,
        margin_b=120, margin_l=50, margin_r=50,
        )
    if streamlit:
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig.show()
    return posts.reset_index(drop=True), fig