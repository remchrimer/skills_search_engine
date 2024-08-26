echo "BUILD START"
python3.12 -m venv venv
source venv/bin/activate
pip install django
pip install -r requirements.txt
python3.12 manage.py migrate
python3.12 manage.py collectstatic
echo "BUILD END"