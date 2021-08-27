# Publish package in PyPi repositories - triggered for new release
python -m pip install --upgrade pip
pip install setuptools wheel twine
python setup.py sdist bdist_wheel
twine upload dist/*
