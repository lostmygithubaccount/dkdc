import requests
import os
import tempfile
import zipfile


def download_and_unzip(uri, datadir):
    r = requests.get(uri)
    with tempfile.TemporaryDirectory() as dir:
        model_zip_path = os.path.join(dir, 'model.zip')
        with open(model_zip_path, 'wb') as output:
            output.write(r.content)
        zip_ref = zipfile.ZipFile(model_zip_path, 'r')
        zip_ref.extractall(datadir)
        zip_ref.close()
        os.remove(model_zip_path)


if __name__ == "__main__":
    datadir = os.path.expanduser("~/catsanddogs")
    download_and_unzip("https://fpgacheckpoint.blob.core.windows.net/dataset/kagglecatsanddogs_3367a.zip", datadir)
