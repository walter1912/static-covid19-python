# %%
#  import các thư viện cần thiết
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import date
# đọc dữ liệu csv online từ github
base_url='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'
confirmed_df = pd.read_csv(base_url + 'time_series_covid19_confirmed_global.csv')
deaths_df = pd.read_csv(base_url + 'time_series_covid19_deaths_global.csv')
recovered_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')


# %%
#dữ liệu số ca nhiễm tính theo ngày của mỗi quốc gia từ 22/1/20 đến nay (từ lúc công bố dịch)
confirmed_df


# %%
#dữ liệu số ca tử vong tính theo ngày của mỗi quốc gia từ 22/1/20 đến nay (từ lúc công bố dịch)

deaths_df

# %%
#dữ liệu số ca hồi phục theo ngày của mỗi quốc gia trong năm 2020
recovered_df

# %%
# xóa các cột thừa : kinh độ, vĩ độ và cột state (các bang của Mỹ và Ấn Độ,...)
confirmed_df = confirmed_df.drop(columns=['Lat', 'Long', 'Province/State'])
deaths_df = deaths_df.drop(columns=['Lat', 'Long', 'Province/State'])
recovered_df = recovered_df.drop(columns=['Lat', 'Long', 'Province/State'])

# %%
# gộp  các bang/tỉnh vào chung 1 nước và set key là 'Date'
confirmed_df = confirmed_df.groupby(by='Country/Region').aggregate(np.sum).T
confirmed_df.index.name = 'Date'
confirmed_df = confirmed_df.reset_index()
deaths_df = deaths_df.groupby(by='Country/Region').aggregate(np.sum).T
deaths_df.index.name = 'Date'
deaths_df = deaths_df.reset_index()
recovered_df = recovered_df.groupby(by='Country/Region').aggregate(np.sum).T
recovered_df.index.name = 'Date'
recovered_df = recovered_df.reset_index()

# %%
# melt :định nghĩa lại các keys và các values của dataframe
# đổi tên cột giá trị thành tên thuộc tính tương ứng
confirmed_melt_df = confirmed_df.melt(id_vars='Date').copy()
confirmed_melt_df.rename(columns={'value':'Confirmed'}, inplace=True)

deaths_melt_df = deaths_df.melt(id_vars='Date')
deaths_melt_df.rename(columns={'value':'Deaths'}, inplace=True)

recovered_melt_df = recovered_df.melt(id_vars='Date')
recovered_melt_df.rename(columns={'value':'Recovered'}, inplace=True)

# %%
# chuyển từ date dạng string sang Date
confirmed_melt_df['Date'] =pd.to_datetime(confirmed_melt_df['Date'])
# chuyển date về dạng ngày/tháng/năm cho tiện theo dõi
confirmed_melt_df['Date']=confirmed_melt_df['Date'].dt.strftime('%d/%m/%Y')

deaths_melt_df['Date'] =pd.to_datetime(deaths_melt_df['Date'])
deaths_melt_df['Date']=deaths_melt_df['Date'].dt.strftime('%d/%m/%Y')

recovered_melt_df['Date'] =pd.to_datetime(recovered_melt_df['Date'])
recovered_melt_df['Date']=recovered_melt_df['Date'].dt.strftime('%d/%m/%Y')

# lấy ra ngày cập nhật mới nhất của dữ liệu
max_date = confirmed_melt_df.Date[confirmed_melt_df['Date'].index.max()]


# %%
max_date

# %%
# vì dữ liệu số ca bệnh hồi phục ko được cập nhật đầy đủ nên sử dụng dữ liệu ca nhiễm và dữ liệu ca tử vong
# lấy danh sách ngày cuối cùng cập nhật dữ liệu
last_confirmed = confirmed_melt_df[confirmed_melt_df['Date'] == max_date]
last_deaths = deaths_melt_df[deaths_melt_df['Date'] == max_date]



# %%
# tính tổng tất cả ca nhiễm và ca tử vong trên toàn thế giới
total_confirmed = last_confirmed['Confirmed'].sum()
total_deaths = last_deaths['Deaths'].sum()


# %%
# tạo khung nội dung tổng
fig_total = go.Figure()
fig_total.add_trace(go.Indicator(
    mode='number', value=int(total_confirmed), 
    number={'valueformat':'0,f'}, 
    title={'text':'Tổng số ca nhiễm'}, 
    domain={'row':0,'column':0}
))
fig_total.add_trace(go.Indicator(
    mode='number', value=int(total_deaths), 
    number={'valueformat':'0,f'}, 
    title={'text':'Tổng số ca tử vong'}, 
    domain={'row':1,'column':0}
))
fig_total.update_layout(grid={'rows':2,'columns':1, 'pattern':'independent'})

# %%
# tổng số ca nhiễm của 20 nước đầu tiên xếp theo bảng chữ cái 
fig = px.bar(last_confirmed.head(20), x = 'Country/Region', y='Confirmed')
fig.show()

# %%
# sắp xếp theo toonge số ca nhiễm của các nước từ cao đến thấp và lấy dữ liệu của 20 nước đầu tiên
last_confirmed_top = last_confirmed.sort_values('Confirmed', ascending=False).head(20)
fig = px.bar(last_confirmed_top,
 x = 'Country/Region', y='Confirmed', text='Confirmed')
fig.show()

# %%
# tạo dữ liệu số ca nhiễm và số ca tử vong của việt nam tính theo ngày
# fig3 = px.line(confirmed_melt_df[confirmed_melt_df['Country/Region']=='Vietnam'], x='Date', y='Confirmed')

vietnam = confirmed_melt_df[confirmed_melt_df['Country/Region']=='Vietnam']
vietnam['Deaths'] = deaths_melt_df['Deaths'][deaths_melt_df['Country/Region']=='Vietnam']
# dùng make_subplots để thể hiện nhiều hơn 1 biểu đồ vào bảng
fig3 = make_subplots(specs=[[{'secondary_y': True}]])
fig3.add_trace(go.Line(
        x=vietnam['Date'], 
        y=vietnam['Confirmed'],
        name='Confirmed')
        , secondary_y=False)
fig3.add_trace(go.Line(
        x=vietnam['Date'], 
        y=vietnam['Deaths'], 
        name='Deaths'), secondary_y=True)
# fig3.update_layout(barmode='lines', xaxis_tickangle=-45)

fig3.show()
vietnam


# %%
# biểu đồ tổng số ca nhiễm của tất cả các nước tính theo ngày
confirmed_scater = px.scatter(confirmed_melt_df,x='Date', y='Confirmed', color='Country/Region')
confirmed_scater.show()

# %%
# tạo map world tổng số ca nhiễm của tất cả các nước trên thế giới
pd.set_option('mode.chained_assignment', None)
map_world = px.choropleth(
    last_confirmed,
    locations='Country/Region', locationmode='country names', 
    color_continuous_scale='dense',
    color=np.log10(last_confirmed['Confirmed']), 
    range_color=(0,10), 
    hover_data=['Confirmed'])
map_world.show()

# %%
# tạo dataframe mới để tính tỉ lệ tử vong/ca nhiễm của tất cả các nước dựa trên dataframe tổng số ca tử vong và ca nhiễm
rate_deaths_df = last_confirmed.copy()
rate_deaths_df['Deaths'] = last_deaths['Deaths']
rate_deaths_df['Rate deaths'] = rate_deaths_df['Deaths']/rate_deaths_df['Confirmed']
rate_deaths_df

# %%
# sắp xếp data frame mới theo số ca tử vong và lấy 20 nước đầu tiên
sort_deaths_df = rate_deaths_df.copy()
sort_deaths_df = sort_deaths_df.sort_values(by='Deaths', ascending=False).head(20)
sort_deaths_df

# %%
# tạo bảng mới kết hợp giữa số ca tử vong và tỉ lệ tử vong của các nước
# dùng make_subplots để gộp biểu đồ
fig = make_subplots(specs=[[{'secondary_y': True}]])
fig.add_trace(go.Bar(
    x=sort_deaths_df['Country/Region'],y=sort_deaths_df['Deaths'], 
    text=sort_deaths_df['Deaths'], 
    name='Deaths',textposition='auto',
),secondary_y=False)
fig.add_trace(go.Scatter(
    x =sort_deaths_df['Country/Region'], 
    y=sort_deaths_df['Rate deaths'], 
    text=sort_deaths_df['Rate deaths'], 
    name='Tỉ lệ tử vong (%)',
    mode='markers+lines',
), secondary_y=True)
fig.show()

# %%
# số ca nhiễm tăng lên mỗi ngày
daily_confirmed_df = confirmed_melt_df.groupby(by='Date').aggregate(np.sum)
daily_confirmed_df.index.name = 'Date'
daily_confirmed_df = daily_confirmed_df.reset_index()
daily_confirmed_df = daily_confirmed_df.sort_values(by='Confirmed')
daily_confirmed_df['Daily Confirmed'] = daily_confirmed_df['Confirmed'].diff()
daily_confirmed_df

# %%
# tạo bảng tổng số ca nhiễm tăng lên mỗi ngày của thế giới
daily_confirmed = px.area(daily_confirmed_df, x='Date', y='Daily Confirmed')
daily_confirmed.show()

# %%
# số ca nhiễm tăng lên mỗi ngày của việt nam
confirmed_melt_df['Daily Confirmed'] = confirmed_melt_df['Confirmed'].diff()
daily_confirmed = px.area(confirmed_melt_df[confirmed_melt_df['Country/Region']=='Vietnam'], x='Date', y='Daily Confirmed')
daily_confirmed.show()

# %%
# lấy data mới để lấy dữ liệu về test covid và vaccine covid
new_base= 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/latest/owid-covid-latest.csv'
data2_df = pd.read_csv(new_base)
test_df = data2_df.copy()
test_df.drop(test_df.columns.difference(['location','total_tests_per_thousand','total_tests', 'population']), 1, inplace=True)
vaccine_df = data2_df.copy()
vaccine_df.drop(vaccine_df.columns.difference(['location','total_vaccinations','people_vaccinated','people_fully_vaccinated', 'population']), 1, inplace=True)

# %%
# dataframe về vaccine 
vaccine_df

# %%
# dataframe về xét nghiệm covid
test_df['vaccine']=vaccine_df['total_vaccinations']
test_df['rate']=test_df['total_tests']/test_df['population']
test_df_top = test_df.sort_values(by='total_tests', ascending=False).head(10) 
test_df

# %%
# tạo bảng kết hợp giữa tổng số lượt xét nghiệm và tỉ lệ lượt xét nghiệm covid trên 1 người dân
rate_test = make_subplots(specs=[[{'secondary_y': True}]])
rate_test.add_trace(go.Bar(
    x = test_df_top['location'],
    y = test_df_top['total_tests'], 
    name='Dân số', 
       marker_color='seagreen'
),secondary_y=False)
rate_test.add_trace(go.Line(
    x = test_df_top['location'],
    y= test_df_top['rate'], 
    name='Tỉ lệ test'
), secondary_y=True)
rate_test.show()

# %%
test_covid = go.Figure()
test_covid.add_trace(go.Bar(
    x=test_df_top['location'], 
    y=test_df_top['total_tests'], 
    name='Tổng số lượt xét nghiệm', 
    marker_color='indianred'
))
test_covid.add_trace(go.Bar(
    x=test_df_top['location'],
    y=test_df_top['vaccine'],
    name='Tổng lượng vaccine trong nước', 
    marker_color='lightsalmon'
))
test_covid.update_layout(barmode='group', xaxis_tickangle=-45)
test_covid.show()

# %%
# tạo dữ liệu về lượng vaccine chưa sử dụng
vaccine_df['reserve']=vaccine_df['total_vaccinations']-vaccine_df['people_vaccinated']
# tạo dữ liệu về những người mới được tiêm một lần
vaccine_df['one_short']=vaccine_df['people_vaccinated']-vaccine_df['people_fully_vaccinated']
# những người chưa được tiêm
vaccine_df['no_vaccine']=vaccine_df['population']-vaccine_df['people_vaccinated']
# sắp xếp dữ liệu mới tạo theo dân số
vaccine_df = vaccine_df.sort_values(by='population', ascending=False)
vaccine_df = vaccine_df.set_index("location")
# xóa dữ liệu của các thuộc tính ko phải là tên quốc gia
vaccine_df = vaccine_df.drop(['World','Low income','Lower middle income', 'Upper middle income','High income', 'Asia', 'Africa', 'Europe','North America','South America','European Union' ])

# %%
# lấy giá trị của 20 nước có dân số đông nhất
vaccine_df_top = vaccine_df.head(20)


# %%
# vaccine_df.reset_index()
#  tạo bảng bar dạng stack
vaccine_covid = go.Figure(go.Bar(
    x=vaccine_df_top.index,
    y=vaccine_df_top['no_vaccine'], 
    name='Số người chưa được tiêm vaccine',
))
vaccine_covid.add_trace(go.Bar(
    x=vaccine_df_top.index, 
    y=vaccine_df_top['one_short'],
    name='Số người mới được tiêm 1 mũi'
))
vaccine_covid.add_trace(go.Bar(
    x=vaccine_df_top.index, 
    y=vaccine_df_top['people_fully_vaccinated'],
    name='Số người đã được tiêm 2 mũi'
))
vaccine_covid.update_layout(
    barmode='stack',
    xaxis={'categoryorder':'total descending'},
    title ='Top 20 nước dân số lớn nhất thế giới')

# %%
# tỉ lệ số người được tiêm vaccine
vaccine_df['rate'] = vaccine_df['people_vaccinated']/vaccine_df['population']
rate_vaccine_df =  vaccine_df.sort_values(by='rate', ascending=False)
# sắp xếp theo tỉ lệ và lấy 20 nước có tỉ lệ cao nhất
rate_vaccine_df = rate_vaccine_df.head(20)

# %%
# biểu đồ top 20 nước có tỉ lệ tiêm vaccine cao nhất
rate_vaccine = make_subplots(
    specs=[[{'secondary_y': True}]])
rate_vaccine.add_trace(go.Bar(
    x=rate_vaccine_df.index,y=rate_vaccine_df['population'], 
    text=rate_vaccine_df['population'], 
    name='Dân số',textposition='auto',
),secondary_y=False)
rate_vaccine.add_trace(go.Scatter(
    x =rate_vaccine_df.index, 
    y=rate_vaccine_df['rate'], 
    text=rate_vaccine_df['rate'], 
    name='Tỉ lệ tiêm vaccine (%)',
    mode='markers+lines',
), secondary_y=True)
rate_vaccine.update_layout(
    title='Top 20 nước có tỉ lệ tiêm vaccine cao nhất'
)
rate_vaccine.show()

# %%
rate_vaccine_df =  vaccine_df.sort_values(by='rate')
rate_vaccine_df = rate_vaccine_df.head(20)

# %%
# biểu đồ top 20 nước có tỉ lệ vvaccine thấp nhất
rate_vaccine = make_subplots(
    specs=[[{'secondary_y': True}]])
rate_vaccine.add_trace(go.Bar(
    x=rate_vaccine_df.index,
    y=rate_vaccine_df['population'], 
    text=rate_vaccine_df['population'], 
    name='Dân số',textposition='auto',
),secondary_y=False)
rate_vaccine.add_trace(go.Scatter(
    x =rate_vaccine_df.index, 
    y=rate_vaccine_df['rate'], 
    text=rate_vaccine_df['rate'], 
    name='Tỉ lệ tiêm vaccine (%)',
    mode='markers+lines',
), secondary_y=True)
rate_vaccine.update_layout(
    title='Top 20 nước có tỉ lệ tiêm vaccine thấp nhất'
)
rate_vaccine.show()


