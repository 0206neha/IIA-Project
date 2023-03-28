import streamlit as st
import pandas as pd
from wordcloud import WordCloud
from collections import Counter
import plotly.express as px

# Define a function to filter the dataframe based on user input
def filter_dataframe(df, choices,operator):
    print(len(choices))
    # filtered_df = df[df['Tags (Semicolon Separated)'].str.contains(choices[0]) & df['Tags (Semicolon Separated)'].str.contains(choices[1])]
    if operator=='AND':
        opt='&'
    else:
        opt='|'
    filter_string = opt.join([f"df['Tags (Semicolon Separated)'].str.contains('{tag}')" for tag in choices])
    print(filter_string)
    filtered_df = df[eval(filter_string)]
    return filtered_df

def generate_word_cloud(all_tags):
    word_cloud_dict = Counter(all_tags)
    wordcloud = WordCloud(width=800, height=500, background_color='white', min_font_size=10).generate_from_frequencies(
        word_cloud_dict)
    return wordcloud

# Define the Streamlit app

# Set the title and description of the app
st.title("Excel File Filter IIA")
st.write("This app allows you to filter an Excel file based on multiple the tags extracted from the excel file")

# Create a file uploader
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

# If a file is uploaded, read it into a Pandas dataframe
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, index_col=False)

    # st.write("Total Number of Startups: ",len(df),{"font-size": "24px"})

    st.markdown(f"<h3 style='font-size:20px;'>Total Number of Startups: {len(df)}</h3>", unsafe_allow_html=True)

    stage_counts = df["Stage"].value_counts()

    total_startups = len(df)
    percentages = [count / total_startups for count in stage_counts]

    # Create pie chart
    st.markdown("<h3 style='font-size:20px;'>Distribution of startups by stage</h3>", unsafe_allow_html=True)

    fig = px.pie(
        values=percentages,
        names=stage_counts.index,
        # title="Distribution of Startups by Stage"
    )

    st.plotly_chart(fig)

    all_tags = [tag.strip() for tags in df['Tags (Semicolon Separated)'].str.split(';') for tag in tags]
    print(len(all_tags))

    # Create a set of unique tags

    unique_tags = set(all_tags)
    print(len(unique_tags))
    # Generate the word cloud
    wordcloud = generate_word_cloud(all_tags)

    # Display the word cloud
    st.markdown("<h3 style='font-size:20px;'>Word Cloud of Tags</h3>", unsafe_allow_html=True)

    st.image(wordcloud.to_array())


    # Create a multiselect widget for the user to select multiple choices
    st.markdown("<h3 style='font-size:20px;'>Filter Data</h3>", unsafe_allow_html=True)

    choices = st.multiselect("Select choices", unique_tags)
    
    # Create a button to filter the dataframe only if all choices are selected
    if len(choices) != 0:

        # selecting operator for applying filter
        option = st.selectbox('Which operation would you like to apply for filtering tags?',('AND','OR')) or 'AND'

        if st.button("Filter Table"):
            filtered_df = filter_dataframe(df, choices,option)

            new_df = filtered_df[['\nStart up Name', 'IIA Registration Date', 'Stage', 'Tags (Semicolon Separated)', 'Description']]
            # #remove the timestamp

            new_df = new_df.reset_index(drop=True)

            hide_dataframe_row_index = """
                        <style>
                        .row_heading.level0 {display:none}
                        .blank {display:none}
                        </style>
                        """
          
            # Define CSS styles
            card_style = """
            <style>
            .card {
                display: flex;
                flex-direction: column;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
                margin: 10px;
                padding: 10px;
                color:black;
            }

            .card:hover {
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
            }

            .row {
                display: flex;
                flex-direction: row;
                justify-content: space-between;
            }

            .col {
                display: flex;
                flex-direction: column;
            }

            .col-1 {
                flex: 1;
                margin-right: 10px;
            }

            .col-2 {
                flex: 2;
                margin-right: 12px;
            }

            .col-3 {
                flex: 1;
            }

            .tags {
                margin-top: 10px;
                display: flex;
                flex-wrap: wrap;
            }

            .tag {
                background-color: #eee;
                padding: 5px;
                margin-right: 5px;
                margin-bottom: 5px;
                border-radius: 5px;
            }

            .description {
                margin-top: 10px;
            }

            .expand:hover {
                text-decoration: underline;
            }
            </style>
            """
                #             .description {
                #     margin-top: 10px;
                #     height: 100px;
                # }

            # Inject CSS with Markdown
            st.markdown(card_style, unsafe_allow_html=True)

            # Iterate over the rows of the filtered dataframe
            for index, row in filtered_df.iterrows():
                # Create the HTML for the card
                card = """
                <div class="card">
                    <div class="row">
                        <div class="col col-1">
                            <p><strong>Company Name:</strong> {}</p>
                        </div>
                        <div class="col col-2">
                            <p><strong>Registration Date:</strong> {}</p>
                        </div>
                        <div class="col col-3">
                            <p><strong>Stage:</strong> {}</p>
                        </div>
                    </div>
                    <div class="tags">
                        <p><strong>Tags:</strong></p>
                        {}
                    </div>
                    <div class="description">
                        <p><strong>Description:</strong> {}</p>
                    </div>
                </div>
                """.format(row['\nStart up Name'], row['IIA Registration Date'], row['Stage'], 
                        ''.join(['<div class="tag">{}</div>'.format(tag.strip()) for tag in row['Tags (Semicolon Separated)'].split(';')]),
                        row['Description'])

                # Render the card as HTML
                st.markdown(card, unsafe_allow_html=True)


               
    else:
        st.write("Please select at least one choice to filter the dataframe.")
    

    st.markdown("<h3 style='font-size:20px;'>Tags and its count</h3>", unsafe_allow_html=True)



    # Create a pandas DataFrame with the tags and their count
    df_tags = pd.DataFrame({'tag': all_tags})
    df_tags = df_tags.groupby(['tag']).size().reset_index(name='count')

    # Sort the DataFrame by count in descending order
    df_tags = df_tags.sort_values('count', ascending=False)

    # Reset the index to start from 1
    df_tags = df_tags.reset_index(drop=True)
    df_tags.index += 1

    # Create a pagination for the table
    PAGE_SIZE = 10
    num_pages = len(df_tags) // PAGE_SIZE + 1
    page_number = st.number_input('Page Number', min_value=1, max_value=num_pages, value=1)

    # Display the table for the selected page
    start_index = (page_number - 1) * PAGE_SIZE
    end_index = page_number * PAGE_SIZE
    st.table(df_tags.iloc[start_index:end_index][['tag', 'count']])
