echo "BUILD START"
python3.9 -m venv venv
source venv/bin/activate
pip install django
echo "TESTING 1"
pip install -r requirements.txt
echo "TESTING 2"
python3.9 manage.py migrate
python3.9 manage.py collectstatic
echo "BUILD END"