from django.core.management.base import NoArgsCommand
from django.utils.crypto import get_random_string
from django.conf import settings
import os, re

regex = re.compile("SECRET_KEY\s*=\s*'(.*)'", re.IGNORECASE)

class Command(NoArgsCommand):
    help = "Reset SECRET_KEY for this project"
    def handle_noargs(self, **options):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        new_key = get_random_string(100, chars)
        private_file = settings.GENERAL_DIR
        for directory in ['settings', 'private.py']:
            private_file = os.path.join(private_file, directory)
        with open(private_file) as f:
            old_data = f.read()
        f = open(private_file, 'w')
        m = regex.search(old_data)
        if m:
            f.write(old_data[0:m.start(1)] + new_key + old_data[m.end(1):])
        else:
            f.write(old_data)
        f.close()
        
