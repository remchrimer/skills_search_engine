echo "BUILD START"
python3.9 -m venv venv
source venv/bin/activate
#python3.9 -m pip install --upgrade pip
pip install django
python3.9 -m pip install -r requirements.txt
python3.9 manage.py migrate
python3.9 manage.py collectstatic
echo "BUILD END"