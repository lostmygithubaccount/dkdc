# get_data script that gets executed on the remote cluster at AutoML Runtime
def get_data():
    from sklearn import datasets
    digits = datasets.load_digits()

    # Exclude the first 100 rows from training so that they can be used for test.
    X_train = digits.data[100:, :]
    y_train = digits.target[100:]
    X_valid = digits.data[:100, :]
    y_valid = digits.target[:100]

    return {"X": X_train, "y": y_train, "X_valid": X_valid, "y_valid": y_valid}
