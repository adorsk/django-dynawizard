virtualenv-3.4 venv3.4

source venv3.4/bin/activate

pip install -r requirements.txt

cd dynawizard_project

python manage.py migrate


