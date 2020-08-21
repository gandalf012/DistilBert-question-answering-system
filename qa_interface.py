""" Testing Scrapping result on cdqa """

import streamlit as st
import pandas as pd
import time, re, os
import json

from multiprocessing import freeze_support

from cdqa.utils.download import download_model
from cdqa.pipeline.cdqa_sklearn import QAPipeline

HTML_WRAPPER = """<span style = "overflow-x: auto;
                                 color : white;
                                 background-color: rgb(246, 51, 102);
                                 border: 1px solid #e6e9ef;
                                 border-radius: 0.4rem;
                                 padding: 0.2rem;
                                 margin-bottom: 2.5rem">{}</span>"""


HTML_PG_WRAPPER = """<div style = "
                        overflow-y: auto; 
                        background-color: rgba(0, 104, 201, 0.1); 
                        border-radius: 5px; 
                        border: 1px solid #ced7de; 
                        padding:20px; 
                        height: 260px; 
                        max-height: 265px
                        margin: 0 0 1rem;">{}</div>"""


# Load the models out of the main 
@st.cache(allow_output_mutation=True)
def get_bert_model():
    if not os.path.exists('./models'):
        os.makedirs('./models')
    if not os.path.exists('./models/bert_qa.joblib'):
        download_model(model="{}-squad_1.1".format('bert'), dir='./models')
    return QAPipeline(reader='./models/bert_qa.joblib', max_df=1.0, min_df=1)

@st.cache(allow_output_mutation=True)
def get_distilbert_model():
    if not os.path.exists('./models'):
        os.makedirs('./models')
    if not os.path.exists('./models/distilbert_qa.joblib'):
        download_model(model="{}-squad_1.1".format('distilbert'), dir='./models')
    return QAPipeline(reader='./models/distilbert_qa.joblib', max_df=1.0, min_df=1)


if __name__ == "__main__":
    freeze_support()

    st.title("BERT QA System")
    st.info("This is a demonstrator of the potential of our Question Answer system. \
              \n- Select first a **Database** \
              \n- Choose an **article** and **Ask a question about it** to admire the result ! \N{bird}")

    # sidebar options    
    st.sidebar.title("Navigation")
    langu = st.sidebar.selectbox("Langue", ["English", "French"])
    model = st.sidebar.selectbox("Model", ["DistilBert", "Bert"])
    source = st.sidebar.selectbox("Database", ["Burberry", "Chanel", "De Witt", "Dior", "Gucci", "Louis Vuitton"])


    with open('./data/{}.json'.format(source.replace(" ", "_"))) as json_file:
        data = json.load(json_file)

    data = pd.DataFrame(data) 
    indexes = range(0, len(data))
    mapper = lambda x: data.loc[x, 'title']
    ind = st.selectbox("Choose an article", options = indexes, index= 1, format_func = mapper)
    st.subheader("Ask a question about this article")
    paragraphs_html = '\n'.join(["""<p>{}<p>""".format(p) for p in data.loc[ind,'paragraphs'] if p.strip()])
    st.write(HTML_PG_WRAPPER.format(paragraphs_html), unsafe_allow_html= True)
    
    default_query = "Write your question here..."
    para = data.loc[ind,'paragraphs']
    df = pd.DataFrame([[0, 'My paragraph', para]], columns=['id', 'title', 'paragraphs']) 


    ### MODEL TRAINING SECTION
    s1 = time.time()

    qa_model = None
    if "DistilBert" in model:
        if "English" in langu:
            qa_model = get_distilbert_model()
        else:
            st.error("French models are not available at the moment")
    else:
        if "English" in langu:
            qa_model = get_bert_model()
        else:
            st.error("French models are not available for the moment")

    t1 = time.time() - s1

    # Fitting the retriever to the list of documents in the dataframe$
    s2 = time.time()
    qa_model.fit_retriever(df)
    t2 = time.time() - s2

    # Querying and displaying 
    query = st.text_input(label="", value=default_query)
    if st.button("Predict answers") and query != default_query: 
        s3 = time.time()
        prediction = qa_model.predict(query)
        t3 = time.time() - s3
        
        st.success(prediction[0]) 

        res = prediction[2].replace(prediction[0], HTML_WRAPPER.format(prediction[0]))
        st.subheader("Article containing the answer:")
        st.write('*{}*\n'.format(res), unsafe_allow_html=True)
        st.info('Answering your question required **{} seconds**.'.format(round(t3, 2)))

    else: 
        st.error("You need **ask a question** and **press the button** to predict the answer")

