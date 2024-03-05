# -*- coding: utf-8 -*-
"""PCA analysis for EIS features.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wAcQ9OUNqDS_uZJG5gvE5AtQ-6QqTFJ0

PCA analysis for generated features from P180_2,3,4 and P190_2,3,4

To plot cyclic voltammetry data from different subfolders
"""

from google.colab import drive
drive.mount('/content/drive', force_remount=True)

import pandas as pd
import glob
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from tables.table import Column
import seaborn as sns
import scipy.stats
import plotly.express as px
from IPython.display import clear_output
from scipy.interpolate import interp1d

#set working directory containg the Data
os.chdir('/content/drive/Shareddrives/R&D/Projects/DataforManuscript/')

#!pip install plotly

"""#Import processed EIS features and clean the data"""

# read generated features from the folder Generated Folders and store the featrues in Feature_dict
Feature_dict={}

for pack in ['P190_02','P190_03','P190_04','P180_02','P180_03','P180_04']:
  files=glob.glob(os.path.join('Generated Features',  pack+'*'))
  Feature_dict[pack]=pd.read_csv(files[-1]).set_index('Unnamed: 0')

#populate features from all packs into one dataframe
feature_names=["xofymax","intercept","diameter","tailhead","slope","shape","shoulder","ymax","pack","scan","cell","xofymax-intercept","tailhead-intercept","shoulder-intercept"]
dict={}

for pack in ['P190_02','P190_03','P190_04','P180_02','P180_03','P180_04']:
  dict[pack]=pd.DataFrame(columns=feature_names)
  for i in range(0,8):
    t=Feature_dict[pack][0+5*i:5+5*i].melt()
    t=t.set_index(pd.Index([pack+"_"+"cell"+str(j%5+1)+"_"+"scan"+"{:02d}".format(j//5+1) for j in range(0,len(t["variable"]))]))
    t=t.drop("variable",axis=1)
    #t.columns=[feature_names[i]]
    dict[pack][feature_names[i]]=t

  #add pack, cell, scan to df_features
  dict[pack]["pack"]=pack
  dict[pack]["scan"]=[ "scan"+"{:02d}".format(j//5+1) for j in range(0,len(t))]
  dict[pack]["cell"]=[ "cell"+str(j%5+1) for j in range(0,len(t))]

  #subtract intercept from xofymax, tailhead, shoulder
  dict[pack]["xofymax-intercept"]=dict[pack]["xofymax"]-dict[pack]["intercept"]
  dict[pack]["tailhead-intercept"]=dict[pack]["tailhead"]-dict[pack]["intercept"]
  dict[pack]["shoulder-intercept"][dict[pack]["shoulder"]!=0]=dict[pack]["shoulder"][dict[pack]["shoulder"]!=0]-dict[pack]["intercept"][dict[pack]["shoulder"]!=0]

df_features=pd.concat([dict[pack] for pack in ['P190_02','P190_03','P190_04','P180_02','P180_03','P180_04']])

#set zero values to NaN in the dataframe
df_features[df_features==0]=float('NaN')
df_features

featuresToPlot=df_features
#discard points with shape outliers
featuresToPlot.loc[abs(featuresToPlot["shape"]-1.36)>0.2]=float('NaN')

# plot features and color by packs
sns.set(font_scale=1.2)
sns.set_style("whitegrid", {'axes.grid' : False})
sns.set_style({'axes.edgecolor': 'black'})
fig=sns.pairplot(featuresToPlot,diag_kind="kde",\
             x_vars=["xofymax-intercept","diameter","tailhead-intercept","slope","shape","ymax"],\
             y_vars=["xofymax-intercept","diameter","tailhead-intercept","slope","shape","ymax"],\
             hue="pack",size=2, markers = ['o', "^","v","s","d","p"],corner=True)
fig.savefig("Figures/Feautre_pairplot.png")

"""#PCA"""

from sklearn.preprocessing import scale
from sklearn import model_selection
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

#define predictor and response variables
X = featuresToPlot[["xofymax-intercept","diameter","tailhead-intercept","slope","shape","ymax"]].dropna()

#scale X and apply PCA
X_scaled= StandardScaler().fit_transform(X)

pca = PCA(n_components=2)

principalComponents = pca.fit_transform(X_scaled)

principalDf = pd.DataFrame(data = principalComponents
             , columns = ['principal component 1', 'principal component 2'])

principalDf=principalDf.set_index(X.index)

explained_variance = pca.explained_variance_ratio_
explained_variance

fig = plt.figure(figsize = (4,4))
ax = fig.add_subplot(1,1,1)
ax.set_xlabel('Principal Component 1', fontsize = 15)
ax.set_ylabel('Principal Component 2', fontsize = 15)
ax.set_title('2 component PCA', fontsize = 20)


targets = ['P190_02','P190_03','P190_04','P180_02','P180_03','P180_04'] # to plot before or after
colors = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown']
labels=['o', "^","v","s","d","p"]
for target, color,label in zip(targets,colors,labels):
    indicesToKeep = principalDf.index.str.contains(target)
    ax.scatter(principalDf.loc[indicesToKeep, 'principal component 1']
               , principalDf.loc[indicesToKeep, 'principal component 2']
               , c = color,marker=label
               , s = 50)
ax.legend(targets,bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
fig.savefig("Figures/Feautre_PCA.png")

