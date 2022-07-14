
# ======================================================================================================================
# Imports
# ======================================================================================================================

# generic imports
import os, time, json
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 150)
pd.set_option('display.min_rows', 150)
from tqdm import tqdm
from datetime import datetime
from pathlib import Path
import joblib
from joblib import dump, load

# modeling utilities
from sklearn.model_selection import train_test_split
from sklearn.base import clone, BaseEstimator, TransformerMixin
from sklearn.compose import make_column_transformer, ColumnTransformer, make_column_selector
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler, RobustScaler, MinMaxScaler, PolynomialFeatures, PowerTransformer, FunctionTransformer
import category_encoders as ce

# unsupervised learning
from sklearn.decomposition import PCA
from sklearn.cluster import FeatureAgglomeration, AgglomerativeClustering, KMeans

# feature selection
from sklearn.feature_selection import SelectKBest,SelectFromModel,VarianceThreshold,RFE,SequentialFeatureSelector,mutual_info_classif,chi2
from xverse.ensemble import VotingSelector
from boruta import BorutaPy

# classification specific imports
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import classification_report, confusion_matrix, make_scorer
from sklearn.metrics import log_loss, average_precision_score, accuracy_score, roc_auc_score, f1_score, recall_score, precision_score
from mlxtend.evaluate import lift_score

# balancing
from imblearn.over_sampling import SMOTE,RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler,TomekLinks
from imblearn.combine import SMOTEENN,SMOTETomek
from imblearn.pipeline import Pipeline as imbPipeline
from imblearn.metrics import classification_report_imbalanced

# training
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingRandomSearchCV, HalvingGridSearchCV
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_predict,cross_val_score, cross_validate
import optuna

from sklearn import set_config
set_config(display="diagram")

# misc
import matplotlib.pyplot as plt
import scikitplot as skplt


# ======================================================================================================================
# Custom Functions
# ======================================================================================================================

def clf_metrics(fitted_object, X, y):
    y_pred_labels = fitted_object.predict(X)
    y_pred_probas = fitted_object.predict_proba(X)
    # metrics
    results = {
    'accuracy' : accuracy_score(y, y_pred_labels),
    'roc' : roc_auc_score(y, y_pred_labels),
    'precision' : precision_score(y, y_pred_labels),
    'recall' : recall_score(y, y_pred_labels),
    'f1' : f1_score(y, y_pred_labels),
    'lift' : lift_score(y, y_pred_labels),
    'log_loss' : log_loss(y, y_pred_probas),
    'prauc' : average_precision_score(y, y_pred_probas[:,1]),
    'confusion' : confusion_matrix(y,y_pred_labels)
    # # plots
    # skplt.metrics.plot_roc(y_test, y_proba_test)
    # skplt.metrics.plot_cumulative_gain(y_test, y_proba_test)
    # skplt.metrics.plot_precision_recall(y_test, y_proba_test)
    # skplt.metrics.plot_confusion_matrix(y_test, y_preds_test, normalize=True)
    # skplt.metrics.plot_ks_statistic(y_test, y_proba_test)
    # skplt.metrics.plot_calibration_curve(y_test, [y_proba_test])
    # plt.show()
    # plt.savefig("mygraph.png")
    }
    # reports
    print()
    print(classification_report_imbalanced(y, y_pred_labels))
    print()
    print(classification_report(y, y_pred_labels))
    return results


def pipeline_from_string(pipestring):

    '''
    :param pipestring: provide a string to create a pipeline ;
        <numeric_features_processing>...............................select from : 'robust', 'power', 'standard'
        <categorical_features_processing>...........................select from : 'ordinal', 'target', 'onehot'
        <variance threshold (optional)>.............................select from : 'variance' or omit
        <feature_selection (optional)>..............................select from : 'pca' or 'model_select' which will be deducted based on estimator selection
        <sampling or cost-sensitive learning (optional)>............select from : 'smote', 'oversampling', 'undersampling' or'csl' which will be used to adjust estimator
        <estimator>.................................................select from : 'lr' or 'lgbm'
        * example 'power,target,variance,select_lr,smote,lr'
    :return: pipeline object
    '''

    # prepare selectors for pipeline
    num_selector = make_column_selector(dtype_include=np.number)
    cat_selector = make_column_selector(dtype_include=object)

    # ==================================================================================================================
    # numeric transformer
    # ==================================================================================================================

    if 'standard' in pipestring:
        numeric_transformer = Pipeline(steps=[
            ('numeric_imputer', SimpleImputer(strategy='median')),
            ('standard_scaler', StandardScaler())])
    elif 'robust' in pipestring:
        numeric_transformer = Pipeline(steps=[
            ('numeric_imputer', SimpleImputer(strategy='median')),
            ('robust_scaler', RobustScaler())])
    elif 'power' in pipestring:
        numeric_transformer = Pipeline(steps=[
            ('numeric_imputer', SimpleImputer(strategy='median')),
            ('power_transformer', PowerTransformer())])

    # ==================================================================================================================
    # categorical transformer
    # ==================================================================================================================

    if 'ordinal' in pipestring:
        categorical_transformer = Pipeline(steps=[
            ('categorical_imputer', SimpleImputer(strategy='most_frequent')),
            ('ordinal_encoder', ce.OrdinalEncoder())])
    elif 'target' in pipestring:
        categorical_transformer = Pipeline(steps=[
            ('categorical_imputer', SimpleImputer(strategy='most_frequent')),
            ('target_encoder', ce.TargetEncoder())])
    elif 'onehot' in pipestring:
        categorical_transformer = Pipeline(steps=[
            ('categorical_imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot_encoder', OneHotEncoder(drop='first',handle_unknown='ignore'))])

    # ==================================================================================================================
    # preprocessor
    # ==================================================================================================================

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_selector),
            ('cat', categorical_transformer, cat_selector)])

    pipeline_list = [('preprocessor', preprocessor)]

    # ==================================================================================================================
    # variance (optional)
    # ==================================================================================================================

    if 'variance' in pipestring:
        pipeline_list.append(('variance',VarianceThreshold()))

    # ==================================================================================================================
    # feature selection (optional)
    # ==================================================================================================================

    if 'model_select' in pipestring:
        if 'lr' in pipestring:
            pipeline_list.append(('feature_selection', SelectFromModel(LogisticRegression(penalty='l1',solver='saga',max_iter=200,n_jobs=-1))))
        elif 'lgbm' in pipestring:
            pipeline_list.append(('feature_selection', SelectFromModel(LGBMClassifier(n_jobs=-1))))
    elif 'pca' in pipestring:
        pipeline_list.append(('feature_selection', PCA(n_components='mle')))

    # ==================================================================================================================
    # imbalanced learning (optional)
    # ==================================================================================================================

    if 'smote' in pipestring:
        pipeline_list.append(('balancing', SMOTE()))
    elif 'oversampling' in pipestring:
        pipeline_list.append(('balancing', RandomOverSampler()))
    elif 'undersampling' in pipestring:
        pipeline_list.append(('balancing', RandomUnderSampler()))

    # ==================================================================================================================
    # estimator
    # ==================================================================================================================

    if 'lr' in pipestring:
        if 'csl' in pipestring:
            pipeline_list.append(('estimator', LogisticRegression(penalty='l1', solver='saga', max_iter=500, class_weight='balanced', n_jobs=-1)))
        else :
            pipeline_list.append(('estimator', LogisticRegression(penalty='l1', solver='saga', max_iter=500, n_jobs=-1)))
    elif 'lgbm' in pipestring:
        if 'csl' in pipestring:
            pipeline_list.append(('estimator', LGBMClassifier(objective = 'binary', class_weight='balanced', n_jobs=-1)))
        else :
            pipeline_list.append(('estimator', LGBMClassifier(objective = 'binary', n_jobs=-1)))

    # ==================================================================================================================
    # make pipeline
    # ==================================================================================================================

    pipeline = imbPipeline(steps=pipeline_list)
    return pipeline

# ======================================================================================================================
# Prepare Env
# ======================================================================================================================

HOME_FOLDER = Path('D:\GoogleDrive\_projects_\kaizen-churn')
OUTPUT_FOLDER = HOME_FOLDER
OPTUNA_FOLDER = Path(HOME_FOLDER,'optuna')
MODEL_FOLDER = Path(HOME_FOLDER,'estimators')

# load data
X_train = pd.read_pickle(Path(HOME_FOLDER, 'X_train.pkl'))
X_test = pd.read_pickle(Path(HOME_FOLDER, 'X_test.pkl'))
y_train = pd.read_pickle(Path(HOME_FOLDER, 'y_train.pkl'))
y_test = pd.read_pickle(Path(HOME_FOLDER, 'y_test.pkl'))

# prepare scoring metrics
scoring = {
    'accuracy' : make_scorer(accuracy_score),
    'roc' : make_scorer(roc_auc_score),
    # 'precision' : make_scorer(precision_score),
    'recall' : make_scorer(recall_score),
    'f1' : make_scorer(f1_score),
    'lift' : make_scorer(lift_score),
    'log_loss' : make_scorer(log_loss),
    'prauc' : make_scorer(average_precision_score)
    }

# pipe configuration
pipe_config = {
    '1' : 'power,ordinal,variance,model_select,csl,lr',
    '2' : 'robust,onehot,model_select,csl,lr',
    '3' : 'power,onehot,variance,model_select,smote,lr',
    '4' : 'standard,onehot,variance,model_select,csl,lgbm',
    '5' : 'power,onehot,variance,model_select,csl,lgbm',
    '6' : 'robust,target,variance,model_select,undersampling,lgbm'
    }

# ======================================================================================================================
# Read & Manipulate HPO Results
# ======================================================================================================================

colnames = ['fit_time','score_time','test_accuracy','train_accuracy','test_roc','train_roc','test_recall','train_recall',
            'test_f1','train_f1','test_lift','train_lift','test_log_loss','train_log_loss','test_prauc','train_prauc','pipe','timetag','params']

hpo_results = pd.read_csv(Path(OPTUNA_FOLDER,'archive_03','optuna.csv'),header=None)
hpo_results.columns = colnames
hpo_results['params_dict'] = hpo_results.params.apply(lambda x: json.loads(x))

# calculate overfit proxy across core evaluation metrics
for m in ['roc','f1','prauc']:
    hpo_results[f'overfit_proxy_{m}'] = hpo_results[f'train_{m}'] - hpo_results[f'test_{m}']

hpo_results.to_clipboard(index=False)

# aggregate across the k-folds that have run
hpo_results_grp = hpo_results.groupby(['pipe','params','timetag'])[['test_roc','test_f1','test_prauc',
                                                                    'overfit_proxy_roc','overfit_proxy_f1','overfit_proxy_prauc']].agg(['mean'])

hpo_results_grp.columns = ["_".join([x[1],x[0]]) for x in hpo_results_grp.columns]


# filter out results w/ overfit
overfit_threshold = 0.05
hpo_results_clean = hpo_results_grp.reset_index().copy()
hpo_results_clean.shape

for col in [x for x in hpo_results_clean.columns if 'mean_overfit_proxy' in x]:
    hpo_results_clean = hpo_results_clean.query(f"{col} < @overfit_threshold").copy()

hpo_results_clean.shape
hpo_results_clean.columns

# rank overfit and performance across core metrics
for m in ['roc','f1','prauc']:
    hpo_results_clean[f'rank_overfit_{m}'] = hpo_results_clean[f'mean_overfit_proxy_{m}'].rank(ascending=True)
    hpo_results_clean[f'rank_metric_{m}'] = hpo_results_clean[f'mean_test_{m}'].rank(ascending=False)

hpo_results_clean['overall_rank_overfit'] = hpo_results_clean[[x for x in hpo_results_clean.columns if 'rank_overfit_' in x]].sum(axis=1)
hpo_results_clean['overall_rank_metric'] = hpo_results_clean[[x for x in hpo_results_clean.columns if 'rank_metric_' in x]].sum(axis=1)

hpo_results_clean.shape

hpo_results_clean = hpo_results_clean.sort_values(by = ['overall_rank_metric','overall_rank_overfit'])
# hpo_results_clean.to_clipboard(index=False)

select_models_by_timetag = ['2021-11-24@07:31:37','2021-11-24@07:31:52','2021-11-24@05:26:04','2021-11-24@05:19:38']



# ======================================================================================================================
# Fetch configuration and establish model
# ======================================================================================================================

hpo_results_selection = hpo_results_clean.query("timetag in @select_models_by_timetag")
hpo_results_selection['params_dict'] = hpo_results_selection.params.apply(lambda x : json.loads(x))


for index, row in tqdm(hpo_results_selection.iterrows()):

    # parse model configuration
    temp_pipe_str = row['pipe']
    temp_pipe_id = temp_pipe_str[-1]
    temp_pipe = pipeline_from_string(pipe_config.get(temp_pipe_id))
    temp_timetag = row['timetag'].replace('-','').replace(':','').replace('@','_')
    temp_params = row['params_dict']
    temp_model_id = f'{temp_pipe_str}_{temp_timetag}'
    temp_pipe.set_params(**temp_params)

    # evaluate model on the train set
    scores = cross_validate(temp_pipe,X_train,y_train,cv=10,scoring=scoring,return_train_score=True)
    print(scores)

    # fit model and evaluate on test
    temp_pipe.fit(X_train,y_train)
    y_pred_labels = temp_pipe.predict(X_test)
    y_pred_probas = temp_pipe.predict_proba(X_test)
    clf_metrics(temp_pipe,X_test,y_test)

    # save model
    dump(temp_pipe, Path(MODEL_FOLDER,f'{temp_model_id}.joblib'))


