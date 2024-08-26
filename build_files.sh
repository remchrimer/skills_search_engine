echo "BUILD START"
python3.9 -m venv venv
source venv/bin/activate
pip install setuptools
pip install django
pip install -r requirements.txt
python3.9 manage.py migrate
python3.9 manage.py collectstatic
echo "BUILD END"