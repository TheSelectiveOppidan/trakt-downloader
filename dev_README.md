Following rules in [this](https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56)

##Install required packages
Make sure you have the stuff needed to build the release

```python3 -m pip install --user --upgrade setuptools wheel```

```python3 -m pip install twine```

##Build library
Then go to the directory where `setup.py` is and run the following to create the dist files.

```python3 setup.py sdist bdist_wheel```

Then there should be a `/dist` folder with a zip file and a .whl file

##Upload build files
Simple enough it's
```twine upload dist/*```

You'll be asked for username/password but then it should be done!

Have fun!


