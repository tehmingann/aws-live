import sys
import site

site.addsitedir('aws-live/lib/python3.6/site-packages')

sys.path.insert(0, 'aws-live/EmpApp.py')

from app import app as application
