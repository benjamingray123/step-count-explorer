import pandas as pd
import streamlit as st 
import plotly.express as px
import plotly.graph_objects as go
from scipy.signal import find_peaks

@st.cache
def load_data():
    data = pd.read_csv('~/Code/data/dog/DogMoveData.csv') 

    data['DogID_TestNum'] = (data['DogID'].astype(str) + data['TestNum'].astype(str)).astype(int) # aggregate DogID and TestNum 
    data['Behavior'] = data[['Behavior_1', 'Behavior_2', 'Behavior_3']].agg('_'.join, axis=1)   # combine 3 behaviour labels 
   
    data['ANeck_RMS'] = (data['ANeck_x']**2 + data['ANeck_y']**2 + data['ANeck_z']**2)**0.5         # calculate sensor magnitudes 
    data['GNeck_RMS'] = (data['GNeck_x']**2 + data['GNeck_y']**2 + data['GNeck_z']**2)**0.5
    return data

df = load_data()

# ANeck_RMS_prom = df['ANeck_RMS'].std()

st.title('DogMoveData Step Count Explorer')

signal = st.multiselect('Select signals to plot', 
                        ['ANeck_x', 'ANeck_y', 'ANeck_z', 'GNeck_x', 
                         'GNeck_y', 'GNeck_x', 'ANeck_RMS', 'GNeck_RMS'],
                       default=['ANeck_RMS','ANeck_x', 'ANeck_y', 'ANeck_z'])


dogID = st.sidebar.select_slider('Select DogID_TestNum', df['DogID_TestNum'].unique())

behavior = st.selectbox('Select a behavior to plot', sorted(df[df['DogID_TestNum']==dogID]['Behavior'].unique()))

def plot_signal(data, dog, activity, signal):
    fig = px.line(data[(data['DogID_TestNum']==dog) & (data['Behavior']==activity)], x='t_sec', y=signal, hover_name='Behavior')
    return fig 

st.text(f'signal == {signal} \nbehavior == {behavior} \ndogID == {dogID}')
st.plotly_chart(plot_signal(df, dogID, behavior, signal))

dfsubset = df[df['DogID_TestNum']==dogID]['Behavior'].unique().tolist()
gaits = ['Walking', 'Trotting', 'Pacing', 'Galloping']
gait_behaviors = [b for b in dfsubset if any(xb in b for xb in gaits)]

def calc_steps(data, dog, gaits, distance):
    dfdoggait = data.loc[(data['DogID_TestNum']==dogID) & (data['Behavior'].isin([gaits]))]
    
    x = dfdoggait['t_sec'].reset_index(drop=True)
    y = dfdoggait['ANeck_RMS'].reset_index(drop=True)
    p,_ = find_peaks(dfdoggait['ANeck_RMS'], distance=distance, prominence=y.std())
    return x, y, p 

def plot_steps(x, y, p):
    fig = px.line(x=x, y=y)
    fig.add_trace(go.Scatter(x=x[p], y=y[p], mode='markers', name='step'))
    fig.update_layout(
        xaxis_title='t_sec',
        yaxis_title='value')
    return fig 

locomotion = st.selectbox('Select a gait to investigate step counting', sorted(gait_behaviors))
distance = st.slider('Select a value for min distance between peaks (in hundreths of a second increments)', 0, 100, 25)
st.text('note: \ndistance values around 15 (0.15s) appear to work well for trotting gaits. \nwalking gaits typically need a larger distance of ~25 (0.25s)')

x, y, p = calc_steps(df, dogID, locomotion, distance)

st.plotly_chart(plot_steps(x, y, p))
st.text(f'steps identified in this signal: {len(p)} / ???')