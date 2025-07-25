import streamlit as st
import plotly.express as px
import pandas as pd
import os 
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Mesure de dimensions",page_icon=":bar_chart:",layout="wide")
st.title(":bar_chart: Sample SuperStore EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
fl=st.file_uploader(":file_folder: Upload a file ",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename=fl.name
    st.write(filename)
    df=pd.read_excel(filename)
else:
    df=pd.read_excel("Sample - Superstore.xls")
col1 , col2=st.columns((2))
df["Order Date"]=pd.to_datetime(df["Order Date"])
#Getting the min and max date
startdate=pd.to_datetime(df["Order Date"]).min()
enddate=pd.to_datetime(df["Order Date"]).max()
with col1:
    date1=pd.to_datetime(st.date_input("start date",startdate))
with col2:
    date2=pd.to_datetime(st.date_input("end date",enddate))
df=df[(df["Order Date"]>=date1) & (df["Order Date"]<=date2)].copy()

st.sidebar.header("choose your filter : ")
#Create fr region
region=st.sidebar.multiselect("Pick your region", df["Region"].unique())
if not region:
    df2 =df.copy()
else:
    df2=df[df["Region"].isin(region)]
#Create for State
state=st.sidebar.multiselect("Pick the State",df2["State"].unique())
if not state:
    df3=df2.copy()
else:
    df3=df2[df2["State"].isin(state)]
#Create for city
city=st.sidebar.multiselect("Pick the City",df3["City"].unique())
#Filter the data based on region , state and city
if not region and not state and not city:
    filter_df=df
elif not state and not city:
    filter_df=df[df["Region"].isin(region)]
elif not region and not city:
    filter_df=df[df["State"].isin(state)]
elif state and city :
    filter_df=df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city :
    filter_df=df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state :
    filter_df=df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filter_df=df3[df3["City"].isin(city)]
else:
    filter_df=df3[df["Region"].isin(region) & df3["State"].isin(state)& df3["City"].isin(city)]

category_df=filter_df.groupby(by=["Category"],as_index=False)["Sales"].sum()
with col1:
    st.subheader("Category wise sales")
    fig = px.bar(
    category_df,
    x="Category",
    y="Sales",
    text=[f"${x:,.2f}" for x in category_df["Sales"]],
    template="seaborn")
    st.plotly_chart(fig,use_container_width=True,height=200)
with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filter_df, values="Sales",names= "Region",hole=0.5)
    fig.update_traces(text=filter_df["Region"],textposition="outside")
    st.plotly_chart(fig,use_container_width=True)
    cl1,cl2=st.columns((2))
with cl1:
        with st.expander("Category_viewData"):
            st.write(category_df.style.background_gradient(cmap="Blues"))
            csv = category_df.to_csv(index=False).encode('utf-8')
            st.download_button("Dowload Data",data= csv, file_name= "Category.csv",mime="text/csv", help="Click here to dowload the data as a CSV file")


with cl2:
        with st.expander("region_viewData"):
            region=filter_df.groupby(by="Region",as_index=False)["Sales"].sum()
            st.write(region.style.background_gradient(cmap="Oranges"))
            csv = region.to_csv(index=False).encode('utf-8')
            st.download_button("Dowload Data",data= csv, file_name= "Region.csv",mime="text/csv", help="Click here to dowload the data as a CSV file")
filter_df["month_year"]=filter_df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")
linechart = pd.DataFrame(
    filter_df.groupby(filter_df["month_year"].dt.strftime("%Y :%b"))["Sales"].sum()).reset_index()
fig2=px.line(linechart,x="month_year",y="Sales",labels={"Sales":"Amount"},height=500,width=1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)
with st.expander("View Data of TimeSeries"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv= linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Dowload Data',data= csv , file_name="TimeSeries.csv",mime='text/csv')

# Create a tream basend on Region , category , subcategory
st.subheader("Hierarchical view od Sales using TreeMap")
fig3=px.treemap(filter_df,path=["Region","Category","Sub-Category"],values= "Sales",hover_data=["Sales"],color="Sub-Category")
fig3.update_layout(width=800,height=650)
st.plotly_chart(fig3,use_container_width=True)
chart1,chart2=st.columns((2))
with chart1:
    st.subheader("Segment wise Sales")
    fig= px.pie(filter_df,values="Sales",names="Segment",template="plotly_dark")
    fig.update_traces(text=filter_df["Segment"],textposition="inside")
    st.plotly_chart(fig,use_container_width=True)
with chart2:
    st.subheader("Category wise Sales")
    fig= px.pie(filter_df,values="Sales",names="Category",template="gridon")
    fig.update_traces(text=filter_df["Category"],textposition="inside")
    st.plotly_chart(fig,use_container_width=True)


