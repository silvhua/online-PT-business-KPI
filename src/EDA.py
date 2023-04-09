import seaborn as sns
# import matplotlib_inline.backend_inline
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st
from processing import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer

def BoW_eda(df, n=30, text_column='caption', drop=['<number>'], context='paper', title_suffix=None,
        streamlit=False, filename=None, path=r'C:\Users\silvh\OneDrive\data science job search\content'
    ):
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
    if streamlit:
        fig.show()

    if filename:
        try:
            path = f'{path}/'.replace('\\','/')
            fig.savefig(path+filename, bbox_inches='tight')
            print('Saved: ', path+filename)
        except:
            print('Unable to save outputs')
    print('Time completed:', datetime.now())

    return top_n, fig

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

def plot_images_tfidf(input_df, count_vector, kpi='like_count',
        n=5, top=True, max_columns=5, streamlit=False, 
        caption_column='caption', timezone='Canada/Pacific'):
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
        - kpi (str): 'like_count' or 'comments_count'
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

    Updates:
    SH 2023-03-07 16:27: Maintain original index for subsequent indexing of dataframe with the raw data.
    """
    tfidf = tfidf_transform(count_vector)
    ncols = n if n<max_columns else max_columns
    nrows = (n + ncols - 1) // ncols
    secondary_kpi = list(set(['like_count', 'comments_count']) - set(kpi))
    sort_by = [kpi, secondary_kpi[0], 'timestamp']
    # sort_by = ['like_count', 'comments_count', 'timestamp']
    # SH 2023-03-05 21:52
    df = input_df.copy()
    df.columns = df.columns.str.replace(caption_column, f'media_{caption_column}')
    df = pd.concat([df, tfidf], axis=1)

    posts = df.sort_values(by=sort_by, ascending=False if top else True).head(n).copy()
    posts['thumbnail_url'].fillna(posts['media_url'], inplace=True)
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
        title_text=f'Posts with highest {kpi}' if top==True else f'Posts with lowest {kpi}',
        title_xanchor='center', title_x=0.5,
        plot_bgcolor="white", 
        height = 120 + nrows * 300,
        margin_b=120, margin_l=50, margin_r=50,
        )
    if streamlit:
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig.show()
    return posts, fig

def plot_account_insights(
        input_df, agg='sum',
        metric_column_suffix='value', timezone='Canada/Pacific',
        posts_df=None,
        streamlit=False):
    
    """
    2023-03-02 16:07
    """
    df = process_account_insights(input_df, timezone=timezone)
    metrics = df.columns[df.columns.str.contains('_'+metric_column_suffix)].tolist()
    try:
        metrics += ['posts'] if len(posts_df)>0 else ''
    except:
        pass
    metrics = [metric.replace('_'+metric_column_suffix, '') for metric in metrics]
    df.columns = df.columns.str.replace('_'+metric_column_suffix, '')
    groupby_options = ['year-month', 'year-week', 'day_of_week', 'date']
    subplot_titles = [
        f'{metric} per {groupby} ({agg})' for groupby in groupby_options for metric in metrics]
    fig = make_subplots(
        rows=len(groupby_options)*len(metrics), cols=1, subplot_titles=subplot_titles
        )
    row = 1
    xtick_list = []
    df_list = []
    for groupby in (groupby_options):
        df_grouped = df.filter(items=metrics+[groupby]).groupby(
            groupby).agg(agg) if groupby !='date' else df.set_index('date')
        if groupby == 'day_of_week':
            day_names = df.sort_values('day_of_week')['day_of_week_name'].unique()
            df_grouped.index = [day[:3] for day in day_names]
            df_grouped = df_grouped/len(df['year-week'].unique())
        df_list.append(df_grouped)
        for metric in (metrics):
            if (metric == 'posts'):
                print('unique days of the week:', posts_df['day_of_week_name'].unique())               
                posts_grouped = posts_df.filter(items=['caption']+[groupby]).groupby(
                    groupby).agg('count') 
                if groupby == 'date':
                    posts_grouped = posts_grouped.asfreq('D').fillna(0)
                elif groupby == 'day_of_week':
                    day_map = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
                    posts_grouped = posts_grouped.rename(index=day_map)
                    posts_grouped = posts_grouped/(len(df['year-week'].unique()) if agg=='mean' else 1)
            fig.add_trace(
                go.Scatter(
                    y=df_grouped[metric] if metric !='posts' else posts_grouped['caption'],
                    x=df_grouped.index if metric !='posts' else posts_grouped.index, 
                    showlegend=False,
                ),
                row=row, col=1
            )
            row += 1
            if len(df_grouped.index) <= 24:
                xtick_list.append(df_grouped.index if metric != 'posts' else posts_grouped.index)
            else:
                xtick_list.append(None)

    fig.update_layout(
        title_text=f'Insights (periods end at {df.loc[0,"hour"]}:00 {timezone} time)',
        title_xanchor='center', title_x=0.5,
        height = len(groupby_options)*len(metrics) * 200,
        template='plotly'
        )
    # Update the xtick labels for each subplot
    for ax in fig['layout']:
        if ax.startswith('xaxis'):
            subplot = int(ax[5:]) if ax[5:] else 1
            fig['layout'][ax]['tickvals'] = xtick_list[subplot-1]
    if streamlit:
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig.show()
    return fig

def tfidf_top_vs_bottom(data, top_posts, bottom_posts, caption_column='media_caption'):
    """
    Obtain words unique to the top posts and words unique to the bottom posts.

    Parameters:
        - data: DataFrame containing raw data from `get_user_ig_post_text` function
        - top_posts, bottom_posts: DataFrames each containing the top/bottom posts, 
            as determined by `plot_images_tfidf` function
        - caption_column (str): Name of the column containing the post captions. 

    Returns:
        - binary_count_vectorizer (DataFrame): Count vector for the posts (each post is 1 doc).
        - tfidf (DataFrame): Tf-idf vectors, where top posts are pooled into one 
            document and bottom posts are pooled into a 2nd doc.
        - top_posts_words, bottom_posts_words (DataFrames): Words in the corpus that are unique
            to either the top or bottom posts, sorted by highest document frequency. 
    """
    data = data.reset_index(drop=True)
    top_posts_index = top_posts.index
    bottom_posts_index = bottom_posts.index
    select_posts = pd.concat([data.loc[top_posts_index], data.loc[bottom_posts_index]])
    posts_processed, count_vector, vect = post_preprocessing(select_posts)
    binary_count_vectorizer = (count_vector/count_vector).fillna(0).astype(int)
    tfidf = tfidf_transform([ # Pool the top posts into one document and bottom posts into a 2nd doc
        binary_count_vectorizer[:len(top_posts)].sum(), binary_count_vectorizer[len(top_posts):].sum()
        ])
    tfidf.columns = binary_count_vectorizer.columns
    tfidf.index = ['top_posts', 'bottom_posts']
    print(f'Shape of tf-idf vector array: {tfidf.shape}')

    top_posts_words = tfidf.loc['top_posts'][(tfidf.loc['top_posts'] > 0) & (
        tfidf.loc['bottom_posts'] == 0)].sort_values(ascending=False).index.tolist()
    bottom_posts_words = tfidf.loc['bottom_posts'][(tfidf.loc['top_posts'] == 0) & (
        tfidf.loc['bottom_posts'] > 0)].sort_values(ascending=False).index.tolist()
    top_posts_words = pd.DataFrame(
        [(word, binary_count_vectorizer[word].sum()) for word in top_posts_words],
        columns=['word unique to top posts', 'top posts with that word'])
    bottom_posts_words = pd.DataFrame(
        [(word, binary_count_vectorizer[word].sum()) for word in bottom_posts_words],
        columns=['word unique to bottom posts', 'bottom posts with that word'])
    return binary_count_vectorizer, tfidf, top_posts_words, bottom_posts_words