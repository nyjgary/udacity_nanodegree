### Note: Most of the work was done in iPython notebook (see attachment). 
### Included here are the bare minimum code required to test final classifier. 

import sys
import pickle
import numpy as np 
import pandas as pd 
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data
from tester import test_classifier

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi', 'salary', 'total_payments', 'exercised_stock_options',
                 'bonus', 'restricted_stock', 'shared_receipt_with_poi',
                 'total_stock_value', 'expenses', 'other', 
                 'from_this_person_to_poi', 'deferred_income',
                 'long_term_incentive', 'from_poi_to_this_person',
                 'from_this_person_to_poi_pct', 'shared_receipt_with_poi_pct']                 
                      
### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
# 'BHATNAGAR SANJAY' was an outlier that turns out to be due to data entry error
# The data point was kept but values were updated per the PDF 
del data_dict['TOTAL']
data_dict['BHATNAGAR SANJAY']['deferral_payments'] = 0
data_dict['BHATNAGAR SANJAY']['total_payments'] = 137864
data_dict['BHATNAGAR SANJAY']['exercised_stock_options'] = 15456290
data_dict['BHATNAGAR SANJAY']['restricted_stock'] = 2604490
data_dict['BHATNAGAR SANJAY']['restricted_stock_deferred'] = -2604490
data_dict['BHATNAGAR SANJAY']['total_stock_value'] = 15456290
data_dict['BHATNAGAR SANJAY']['expenses'] = 137864
data_dict['BHATNAGAR SANJAY']['other'] = 0
data_dict['BHATNAGAR SANJAY']['director_fees'] = 0


### Task 3a: Create new feature(s)

for person in data_dict: 
    try: 
        data_dict[person]['from_this_person_to_poi_pct'] = float(data_dict[person]['from_this_person_to_poi']) / data_dict[person]['from_messages'] * 100
    except TypeError:
        data_dict[person]['from_this_person_to_poi_pct'] = 'NaN'
    try: 
        data_dict[person]['from_poi_to_this_person_pct'] = float(data_dict[person]['from_poi_to_this_person']) / data_dict[person]['to_messages'] * 100
    except TypeError: 
        data_dict[person]['from_poi_to_this_person_pct'] = 'NaN'
    try: 
        data_dict[person]['shared_receipt_with_poi_pct'] = float(data_dict[person]['shared_receipt_with_poi']) / data_dict[person]['to_messages'] * 100
    except TypeError: 
        data_dict[person]['shared_receipt_with_poi_pct'] = 'NaN'
        

### Task 3b: Fill in missing values 
# Instead of using featureFormat to imput values, I am doing it on my own here 

# Convert to pd dataframe for easy computation of medians 
df = pd.DataFrame.from_dict(data_dict,orient='index')
df.replace("NaN", np.nan, inplace=True) # properly encode null values 

# Impute missing email information using medians 
features_imputed = ['to_messages', 'from_messages', 'from_this_person_to_poi', 'from_poi_to_this_person', 
                    'shared_receipt_with_poi', 'from_this_person_to_poi_pct', 'from_poi_to_this_person_pct',
                    'shared_receipt_with_poi_pct', 'salary', 'bonus']
for variable in features_imputed: 
    df[variable] = np.where(np.isnan(df[variable]), 
                            np.median(df[~np.isnan(df[variable])][variable]), df[variable])
    
# Replace all NaN's in non-Salary/Bonus financial variables 
features_zeroed = ['long_term_incentive', 'deferred_income', 'deferral_payments', 'other', 
                   'expenses', 'director_fees','total_payments', 'exercised_stock_options', 
                   'restricted_stock', 'restricted_stock_deferred', 'total_stock_value'] 
for variable in features_zeroed: 
    df[variable] = np.where(np.isnan(df[variable]),0,df[variable])


### Store to my_dataset for easy export below.

my_dataset = df.to_dict(orient='index') # convert back to dict 
### Extract features and labels from dataset for local testing
#data = featureFormat(my_dataset, features_list, sort_keys = True)
#labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# --- PLEASE SEE PYTHON NOTEBOOK FOR DETAILS, ONLY FINAL CLF INCLUDED BELOW ---- 

from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import make_pipeline

clf = make_pipeline(MinMaxScaler(), 
                    DecisionTreeClassifier(criterion = 'entropy',
                                           max_depth = 6,
                                           max_features = None, 
                                           min_samples_split = 2,
                                           random_state = 42))

test_classifier(clf, my_dataset, features_list, folds = 1000) 

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)