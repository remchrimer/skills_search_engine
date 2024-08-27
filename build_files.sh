echo "BUILD START"
python3.9 -m venv venv
source venv/bin/activate
pip3 install django
echo "TESTING 1"
pip3 install -r requirements.txt
echo "TESTING 2"
python3.9 manage.py migrate
python3.9 manage.py collectstatic
echo "BUILD END"