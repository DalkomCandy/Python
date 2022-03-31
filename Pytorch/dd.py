# Setting X, y
iris = sns.load_dataset('iris')
X = iris.drop('species', axis = 1)

le = LabelEncoder()
y = le.fit_transform(iris['species'].values)

# 랜덤하게 Train & Test을 나누는 작업
[X_train, X_test, y_train, y_test] = train_test_split(X, y, test_size = 0.2, random_state = 777, stratify = y)

sc = StandardScaler() # (X-υ)/σ
sc.fit(X_train)
X_train = sc.transform(X_train) # Training set 표준화, 
X_test = sc.transform(X_test)   # Test set 표준화

acc_train = []
acc_test = []

for k in n_neighbor_range: # n_neighbor_range만큼 K의 변화에 따른 성능 시각화
    # 모델 생성
    knn = KNeighborsClassifier(n_neighbors=k, p=2)
    
    # Train Set을 학습시킨다.
    knn.fit(X_train, y_train)
    
    # Train set에서 오분류를 찾는다.
    y_train_pred = knn.predict(X_train)
    
    acc_train.append(knn.score(X_train, y_train))
    acc_test.append(knn.score(X_test, y_test))

plt.figure(figsize = (15,4))
plt.plot(n_neighbor_range, acc_train, label = "Accuracy of Training Set")
plt.plot(n_neighbor_range, acc_test,  label = "Accuracy of Test Set")
plt.title("Accuracy of Training & Test set")
plt.xlabel("n_neighbors")
plt.ylabel("Validation Accuracy")
plt.legend(['Training Set', 'Test Set'])
plt.show();