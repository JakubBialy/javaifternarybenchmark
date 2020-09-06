import re
import os
import subprocess

txt = subprocess.check_output([os.environ['JAVA_HOME'] + '/bin/java', '-version'], stderr=subprocess.STDOUT).decode('UTF-8').strip()

# jdk_ver = re.search('\"(.*)\"', txt.split('\n')[0]).group(1)
build_ver = re.search(' \(build (.*)\)', txt.split('\n')[1]).group(1)

# print(jdk_ver + ' build:' + build_ver)
print(build_ver)
