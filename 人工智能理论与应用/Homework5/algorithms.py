import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import csv

# Load data
def load_csv_data(filename):
    file = pd.read_csv(filename)

    data = file[['Elevation', 'Aspect', 'Slope', 'Horizontal_Distance_To_Hydrology', 'Vertical_Distance_To_Hydrology',
                 'Horizontal_Distance_To_Roadways', 'Hillshade_9am', 'Hillshade_Noon', 'Hillshade_3pm', 'Horizontal_Distance_To_Fire_Points',
                 'Wilderness_Area1', 'Wilderness_Area2', 'Wilderness_Area3', 'Wilderness_Area4', 'Soil_Type1',
                 'Soil_Type2', 'Soil_Type3', 'Soil_Type4', 'Soil_Type5', 'Soil_Type6',
                 'Soil_Type7', 'Soil_Type8', 'Soil_Type9', 'Soil_Type10', 'Soil_Type11',
                 'Soil_Type12', 'Soil_Type13', 'Soil_Type14', 'Soil_Type15', 'Soil_Type16',
                 'Soil_Type17', 'Soil_Type18', 'Soil_Type19', 'Soil_Type20', 'Soil_Type21',
                 'Soil_Type22', 'Soil_Type23', 'Soil_Type24', 'Soil_Type25', 'Soil_Type26',
                 'Soil_Type27', 'Soil_Type28', 'Soil_Type29', 'Soil_Type30', 'Soil_Type31',
                 'Soil_Type32', 'Soil_Type33', 'Soil_Type34', 'Soil_Type35', 'Soil_Type36',
                 'Soil_Type37', 'Soil_Type38', 'Soil_Type39', 'Soil_Type40']]
    labels = file['Cover_Type']
    data = np.array(data)
    labels = np.array(labels)
    return data, labels

# Load data
def load_csv_test(filename):
    file = pd.read_csv(filename)

    data = file[['Elevation', 'Aspect', 'Slope', 'Horizontal_Distance_To_Hydrology', 'Vertical_Distance_To_Hydrology',
                 'Horizontal_Distance_To_Roadways', 'Hillshade_9am', 'Hillshade_Noon', 'Hillshade_3pm', 'Horizontal_Distance_To_Fire_Points',
                 'Wilderness_Area1', 'Wilderness_Area2', 'Wilderness_Area3', 'Wilderness_Area4', 'Soil_Type1',
                 'Soil_Type2', 'Soil_Type3', 'Soil_Type4', 'Soil_Type5', 'Soil_Type6',
                 'Soil_Type7', 'Soil_Type8', 'Soil_Type9', 'Soil_Type10', 'Soil_Type11',
                 'Soil_Type12', 'Soil_Type13', 'Soil_Type14', 'Soil_Type15', 'Soil_Type16',
                 'Soil_Type17', 'Soil_Type18', 'Soil_Type19', 'Soil_Type20', 'Soil_Type21',
                 'Soil_Type22', 'Soil_Type23', 'Soil_Type24', 'Soil_Type25', 'Soil_Type26',
                 'Soil_Type27', 'Soil_Type28', 'Soil_Type29', 'Soil_Type30', 'Soil_Type31',
                 'Soil_Type32', 'Soil_Type33', 'Soil_Type34', 'Soil_Type35', 'Soil_Type36',
                 'Soil_Type37', 'Soil_Type38', 'Soil_Type39', 'Soil_Type40']]
    data = np.array(data)
    return data

def testLogisticRegression(features, labels, features_test):

    rf2 = LogisticRegression()

    #train
    rf2.fit(features, labels)

    print("average accuracy of using Logistic Regression is:", np.mean(cross_val_score(rf, features, labels, cv=10)))

    #predict
    predict = rf2.predict(features_test)

    # write csv
    with open("all/predict.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Id", "Cover_Type"])
        for i in range(0, len(predict)):
            writer.writerow([(15121 + i), predict[i]])

def testRandomForest(features, labels, features_test):

    acc_list = []
    acc_list2 = []
    max_estimators = 20
    for i in range(max_estimators):

        rf = RandomForestClassifier(n_estimators=i+1, max_features='sqrt')

        acc_list.append(np.mean(cross_val_score(rf, features, labels, cv=5)))
    
    for i in range(max_estimators):

        rf = RandomForestClassifier(n_estimators=i+1,max_features=None)

        acc_list2.append(np.mean(cross_val_score(rf, features, labels, cv=5))) 
    
    plt.style.use("seaborn")
    plt.plot(list(range(1, max_estimators+1)), acc_list, label="max_features='sqrt'")
    plt.plot(list(range(1, max_estimators+1)), acc_list2, label="max_features=None")
    plt.title("The effect of n_estimators on Random Forest", size='xx-large')
    plt.xlabel("n_estimators", size='xx-large')
    plt.ylabel("average accuracy of 5 fold cross validation", size='xx-large')
    plt.legend(fontsize='x-large')
    plt.yticks(size='x-large')
    plt.xticks(list(range(1, max_estimators+1)), size='x-large')
    plt.show()

def testKNN(features, labels, features_test):
    acc_list = []
    acc_list2 = []
    max_neighbors = 20
    for i in range(max_neighbors):
        KNN = sklearn.neighbors.KNeighborsClassifier(n_neighbors=i+1, weights='uniform', metric='minkowski')
        acc_list.append(np.mean(cross_val_score(KNN, features, labels, cv=5)))
    
    for i in range(max_neighbors):
        KNN = sklearn.neighbors.KNeighborsClassifier(n_neighbors=i+1, weights='distance', metric='minkowski')       #, metric_params={'V':features.var(axis=0)}
        acc_list2.append(np.mean(cross_val_score(KNN, features, labels, cv=5)))
    
    plt.style.use("seaborn")
    plt.plot(list(range(1, max_neighbors+1)), acc_list, label="weights='uniform'")
    plt.plot(list(range(1, max_neighbors+1)), acc_list2, label="weights='distance'")
    plt.title("The effect of n_neighbors on K Nearest Neighbors", size='xx-large')
    plt.xlabel("n_neighbors", size='xx-large')
    plt.ylabel("average accuracy of 5 fold cross validation", size='xx-large')
    plt.legend(fontsize='x-large')
    plt.yticks(size='x-large')
    plt.xticks(list(range(1, max_neighbors+1)), size='x-large')
    plt.show()

def testSVM(features, labels, features_test):
    from sklearn.svm import SVC
    acc_dict = {}
    kernels = ['linear', 'poly', 'rbf', 'sigmoid']
    Cs = [1.0, 5.0, 10.0, 50.0, 100.0]
    for kernel in kernels:
        acc_dict[kernel] = []
        for C in Cs:
            svc = SVC(C=C, kernel=kernel, gamma='auto')
            acc_dict[kernel].append(np.mean(cross_val_score(svc, features, labels, cv=5)))
    print(acc_dict)

def testExtratrees(features, labels, features_test):
    from sklearn.ensemble import ExtraTreesClassifier
    acc_list = []
    acc_list2 = []
    max_estimators = 20
    for i in range(max_estimators):
        extc = ExtraTreesClassifier(n_estimators=i+1, max_features=None, n_jobs=-1, random_state=0)
        acc_list.append(np.mean(cross_val_score(extc, features, labels, cv=5)))
    for i in range(max_estimators):
        extc = ExtraTreesClassifier(n_estimators=i+1, max_features='sqrt', n_jobs=-1, random_state=0)
        acc_list2.append(np.mean(cross_val_score(extc, features, labels, cv=5)))
    plt.style.use("seaborn")
    plt.plot(list(range(1, max_estimators+1)), acc_list, label="max_features='None'")
    plt.plot(list(range(1, max_estimators+1)), acc_list2, label="max_features='sqrt'")
    plt.title("The effect of n_estimators on Extra Trees Classifier", size='xx-large')
    plt.xlabel("n_estimators", size='xx-large')
    plt.ylabel("average accuracy of 5 fold cross validation", size='xx-large')
    plt.yticks(size='x-large')
    plt.xticks(list(range(1, max_estimators+1)), size='x-large')
    plt.legend(fontsize='x-large')
    plt.show()

def make_best_classifier(features, labels, features_test):
    from sklearn.ensemble import ExtraTreesClassifier
    extc = ExtraTreesClassifier(n_estimators=100, max_features=None, n_jobs=-1)
    print("5-fold cross validation accuracy of the best classifier(Extratrees): ", np.mean(cross_val_score(extc, features, labels, cv=5)))
    extc.fit(features,labels)
    predict = extc.predict(features_test)

    # write csv
    with open("all/predict.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Id", "Cover_Type"])
        for i in range(0, len(predict)):
            writer.writerow([(15121 + i), predict[i]])

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    arg = parser.add_argument
    arg('--algorithm', choices=['RandomForest', 'LogisticRegression', 'KNN', 'SVM', 'Extratrees'])
    args = parser.parse_args()


    features, labels = load_csv_data('all/train.csv')
    features_test = load_csv_test('all/test.csv')
    features = sklearn.preprocessing.StandardScaler().fit_transform(X=features)
    features_test = sklearn.preprocessing.StandardScaler().fit_transform(X=features_test)
    from sklearn.utils import shuffle
    features, labels = shuffle(features, labels, random_state=0)

    if args.algorithm == 'RandomForest':
        testRandomForest(features, labels, features_test) 

    if args.algorithm == 'KNN':
        testKNN(features, labels, features_test)
    
    if args.algorithm == 'SVM':
        testSVM(features, labels, features_test)
    
    if args.algorithm == 'Extratrees':
        testExtratrees(features, labels, features_test)
    
    make_best_classifier(features,labels,features_test)