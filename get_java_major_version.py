import re
import os
import subprocess

txt = subprocess.check_output([os.environ['JAVA_HOME'] + '/bin/java', '-version'], stderr=subprocess.STDOUT).decode(
    'UTF-8').strip()

is_java_8_or_older = re.search('\"(.*)\"', txt.split('\n')[0]).group(1).split('.')[0] == '1'

if is_java_8_or_older:
    major_version = re.search('\"(.*)\"', txt.split('\n')[0]).group(1).split('.')[1]

    print(major_version)
else:
    major_version = re.sub("\D","",re.search('\"(.*)\"', txt.split('\n')[0]).group(1).split('.')[0])

    print(major_version)
