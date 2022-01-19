import requests,lxml,json,re
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from streamlit_tags import st_tags
from io import StringIO
import time


def newScraper(listOfTopics):
    st.subheader('Progress:')
    my_bar = st.progress(0)
    resultDict = {}
    progress = 0

    # configurations
    headers = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3538.102 Safari/537.36 Edge/18.19582"
    }
    baseURL = 'https://www.scmp.com'

    data = []
    
    for topic in listOfTopics:
        print(topic)
        scrapeURL = f'https://www.scmp.com/topics/{topic}'
        html = requests.get(scrapeURL,headers=headers)
        status_code = html.status_code
        print(status_code)
        if status_code == 200:
            response = html.text
            soup = BeautifulSoup(response, 'lxml')

            print('-----------------------------------')
            articleArea = soup.find('div',class_='article-area')
            allArticles = articleArea.findAll('div',class_='article-level')
            # print(allArticles)
            for article in allArticles:
                # get title 
                title = article.find('div',class_='article__title')
                print(f"Title: {title.text}")

                # get article link 
                a = title.find('a')

                articleURL = baseURL + a['href']
                print(f"Link: {articleURL}")
                print()
                try: 
                    html1 = requests.get(articleURL,headers=headers)
                    response1 = html1.text
                    soup1 = BeautifulSoup(response1, 'lxml')
                    
                    metadata = json.loads("".join(soup1.find("script", text=                                re.compile("articleBody")).contents))

                    # print(json.dumps(metadata, indent=4, sort_keys=True))
                    articleBody = metadata['articleBody']
                    headline = metadata['headline']
                    alternativeHeadline = metadata['alternativeHeadline']
                    dateCreated = metadata['dateCreated']
                    dateModified = metadata['dateModified']
                    datePublished = metadata['datePublished']
                    author = metadata['author']['name']
                    articleURL = metadata['mainEntityOfPage']
                    imageURL = metadata['image']['url']
                    articleSection = metadata['articleSection']

                    subHeadlines = soup1.find('div',class_ = 'info__subHeadline')
                    summaryPoints = subHeadlines.findAll('li',
                    class_='generic-article__summary--li content--li')
                    summary = []
                    for summarypoint in summaryPoints:
                        print(f'- {summarypoint.text}')
                        summary.append(summarypoint.text)

                    # print(f'Published At: {publishedAt.text}')
                except:
                    summary = ''

                data.append([headline,alternativeHeadline,summary,author,articleBody,datePublished,dateCreated,dateModified,articleURL,imageURL,articleSection])
                print('---------------------------------------------')
                # print(len(allArticles))
        progress += (1/(len(listOfTopics)))
        my_bar.progress(progress)

    df = pd.DataFrame(data, columns=['SCMP news headline','alternativeHeadline','Summary Points','Author','Content','Date Published','Date Created','Date Modified','Article Link','Image Link','Section'])
    print(df)
    df.to_csv('SCMPNewsScrapeResults.csv',index=False)


    st.success('SCMP News Scraping completed successfully.')
    return df


def displayScraperResult():
    st.title(':bar_chart: Analysis Visualizer')
    # df = pd.read_csv('SCMPNewsScrapeResults.csv')
    # st.dataframe(df)

    txt = st.text_area('Enter Article Text to Summarize', '''Hong Kong stocks advanced for a third day, as Chinese tech companies rallied in the best winning run in a month on valuations appeal. China Life Insurance and developer Modern Land slumped amid internal financial crises. The Hang Seng Index rose 0.8 per cent to 23,687.10 at the local midday trading break. The Tech Index jumped 2 per cent while China’s Shanghai Composite Index gained 0.3 per cent. Alibaba Health Information surged 12 per cent while Kuaishou Technology rallied 9.7 per cent. Tencent and Meituan added more than 0.9 per cent while Bilibili gained 4.1 per cent, among the biggest winners as tech stocks accumulated about5 per cent gain over three days from an all-time low set on January 5.“Last year’s popular sectors suffered major corrections in the first week of the new year,” Ping An Securities (HK) said in a note on Monday. “But as markets bottom, they present opportunities for investors, given that the Chinese authorities have highlighted they would prioritise economic stability going forward.”The market slump since the end of last year has created buying opportunities as stocks cheapened. Hang Seng Index’s members have been trading below their average book value for 21 straight days. The tech gauge’s price-to-book ratio of 1.36 times is near its record low of 1.29 times set on December 29.A late rally in tech stocks lifted the Hang Seng Index to a 0.4 per cent gain last week. That made it a sixth consecutive year in which the benchmark had a winning opening week to a new year.Elsewhere, China Life Insurance tumbled 1.8 per cent. Its chairman Wang Bin was placed under disciplinary and supervisory investigation, the company said in an exchange filing on Sunday.Modern Land slumped 39 per cent as the stock resumed trading after a three-month halt following several defaults on its offshore debt. The developer said it owed bondholders almost US$1.4 billion and faced legal actions for recovery of payments.Major Asian markets retreated on Monday amid overriding concerns about Covid-19 spread and higher borrowing costs. South Korean equities lost
    ''',height=50)

    # st.write('Sentiment:', run_sentiment_analysis(txt))

    with st.spinner('Wait for it...'):
        time.sleep(5)
    st.success('Done!')
    st.write('Hang Seng Index logged a winning run in three days, the best winning run in a month, as valuations appeal to investors. China Life Insurance and developer Modern Land slumped amid internal financial crises')


# title
st.title(":male-detective: Financial News Summarization")

listOfTopics = ['hong-kong-stock-exchange','hong-kong-economy','china-stock-market','stocks','commodities','regulation','currencies','bonds','stocks-blog','central-banks']

col1, col2 = st.columns(2)

containsUpload = False
with col1:
    st.subheader('Generate SCMP news scraping manually')
    chosen_topics = st_tags(
                label='Add Topics here!',
                text='Press enter to add more',
                value=listOfTopics,
                suggestions=['hong-kong-stock-exchange','hong-kong-economy','china-stock-market','stocks','commodities','regulation','currencies','bonds','stocks-blog','central-banks'],
                key="aljnf"
            )

    st.caption('Current List of Keywords')
    st.write((chosen_topics))

with col2:
    st.subheader('Use your custom dataframe for training')
    uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
    for uploaded_file in uploaded_files:
        # bytes_data = uploaded_file.read()
        st.write("filename:", uploaded_file.name)

        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        dataframe = pd.read_csv(stringio)
        st.write(dataframe)
        containsUpload = True


submitted = st.button("Submit")
    
if submitted:
    if containsUpload:
        st.write('Use Existing Datasets.')
    else:
        st.write('SCMP News Scraping for the following topics: ',str(chosen_topics))
        df = newScraper(chosen_topics)   
    

displayResult = st.button("Display Result")
if displayResult:
    displayScraperResult()
