from kfp.v2.dsl import component, Input, Output, Dataset, Model, Metrics

@component(
    base_image="python:3.9",
    packages_to_install=["pandas", "scikit-learn", "google-cloud-bigquery", "db-dtypes"]
)
def train_tabular_model(
    project: str,
    bq_table: str,
    model: Output[Model],
    metrics: Output[Metrics],
):
    from google.cloud import bigquery
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score
    import pickle

    # 1. Read data from BigQuery
    client = bigquery.Client(project=project)
    query = f"SELECT * FROM `{bq_table}`"
    df = client.query(query).to_dataframe()

    # 2. Prepare data
    # Assuming 'species' is the target and already encoded or we encode it here
    # For simplicity, let's assume 'species' is the label
    X = df.drop("species", axis=1)
    y = df["species"]
    
    # Handle categorical if not handled in Spark (Spark job did some, but let's be safe)
    X = pd.get_dummies(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. Train
    clf = RandomForestClassifier(n_estimators=100)
    clf.fit(X_train, y_train)

    # 4. Evaluate
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    metrics.log_metric("accuracy", acc)

    # 5. Save Model
    model.metadata["framework"] = "scikit-learn"
    with open(model.path + ".pkl", 'wb') as f:
        pickle.dump(clf, f)
