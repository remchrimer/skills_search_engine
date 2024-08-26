echo "BUILD START"
python3.9 -m venv venv
source venv/bin/activate
pip install django
pip install distutils
pip install -r requirements.txt
python3.9 manage.py migrate
python3.9 manage.py collectstatic
echo "BUILD END"