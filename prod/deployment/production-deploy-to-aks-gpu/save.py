import tensorflow as tf
import urllib
import tarfile
import shutil

url = "http://download.tensorflow.org/models/official/"
"20181001_resnet/savedmodels/resnet_v1_fp32_savedmodel_NCHW_jpg.tar.gz"

urllib.request.urlretrieve(
    url,
    "resnet50.tar.gz")
tarfile.open("resnet50.tar.gz", 'r').extractall()
shutil.move("./resnet_v1_fp32_savedmodel_NCHW_jpg/1538686758", "./resnet50")
