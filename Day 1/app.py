import streamlit as st
import pandas as pd

st.title("Student Marks Analysis")

# Upload CSV file
uploaded_file = st.file_uploader("Upload Student Marks CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Uploaded Dataset")
    st.dataframe(df)

    if st.button("Calculate Totals & Averages"):
        df["Total Marks"] = df.iloc[:, 3:].sum(axis=1)
        df["Average Marks"] = df.iloc[:, 3:7].mean(axis=1)

        # Class-wise averages
        class_averages = df.groupby("Class")[df.columns[3:7]].mean()

        # Subject averages across all classes
        subject_averages = df.iloc[:, 3:7].mean()

        st.subheader("Student Data with Totals & Averages")
        st.dataframe(df)

        st.subheader("Class-wise Average in Each Subject")
        st.dataframe(class_averages)

        st.subheader("Subject-wise Average Across All Classes")
        st.write(subject_averages)