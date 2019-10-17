# pip install Sphinx
# if you haven't already

Get-ChildItem docs/generated -Recurse | Remove-Item
Get-ChildItem docs/html -Recurse | Remove-Item -Recurse -Force

sphinx-apidoc -o docs/generated -e src/azureml-core

sphinx-build -b html docs/ docs/html

start docs/html/generated/azureml.html
