import streamlit as st
import pickle
import numpy as np
import pandas as pd

def load_model():
    data = pd.read_pickle('myfile.pkl')
    return data

data = load_model()

def show_sc_page():
    st.title("Scorecard model")

    ## Tạo file uploader (file .csv) và đọc file

    st.write("""### Please upload your file here. Only .csv accepted.""")

    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:   
        customer = pd.read_csv(uploaded_file, header = 0, sep = ',')
        st.write(customer)

        ##Tính điểm tín nhiệm từ file đầu vào
        
        def _search_score(obs, col, frmScore, data):
            feature = [str(inter) for inter in list(data[col]['table'].index) if obs[col].values[0] in inter][0]
            score = frmScore[(frmScore['Columns'] == col) & (frmScore['Features'] == feature)]['Scores'].values[0]
            return score

        def _total_score(obs, columns, frmScore, data):
            scores = dict()
            for col in columns:
                scores[col] = _search_score(obs, col, frmScore, data)
            total_score = sum(scores.values())
            return scores, total_score

        column_cus = ['Name', 'Credit Score', 'Rating']
        frmScore = pd.read_csv('Sccore.csv', header = 0, sep = ',')
        cust_result = []

        columns = ['LOAN', 'MORTDUE', 'VALUE', 'REASON', 'JOB', 'YOJ', 'DEROG', 'DELINQ', 'CLAGE', 'NINQ', 'CLNO', 'DEBTINC']

        #xử lý các dữ liệu số nếu null = 0
        columns_num = customer.select_dtypes(['float', 'int', 'int64']).columns
        customer[columns_num] = customer[columns_num].apply(lambda x: x.fillna(0), axis=0)
        #xử lý dữ liệu object null cho về Missing
        columns_obj = customer.select_dtypes(['object']).columns
        customer[columns_obj] = customer[columns_obj].apply(lambda x: x.fillna('Missing'), axis=0)

        for cus in range(0, len(customer)):
            result = []
            #customer = customer[customer.index == cus]
            #print(customer)
            scores, total_score = _total_score(customer[customer.index == cus], columns , frmScore, data)
            result.append(customer[customer.index == cus]['NAME'].values[0])
            result.append(total_score)

            ## Phân loại rating dựa trên điểm vừa tính

            rating = ""
            if total_score <= 579:
                rating = "Very Poor"
            elif total_score <= 669:
                rating = "Fair"
            elif total_score <= 739:
                rating = "Good"
            elif total_score <= 799:
                rating = "Very Good"
            else:
                rating = "Exceptional"
            
            result.append(rating)

            cust_result.append(result)
            
        frm = pd.DataFrame(cust_result, columns=column_cus)

        def convert_df(df):
            return df.to_csv().encode('utf-8')

        csv = convert_df(frm)

        ## Hiển thị kết quả tính được

        st.write("""### The credit scores are: """)

        st.write(frm)

        ## Tạo nút để download kết quả 

        st.download_button(
        "Please press to download the result",
        csv,
        "Credit_score.csv",
        "text/csv")
    
    