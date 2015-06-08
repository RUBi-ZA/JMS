from subprocess import Popen, PIPE
import getpass, sys

sudo_password = sys.argv[1]

p = Popen("su - rubi -c 'sudo -S ls'", shell=True, stdin=PIPE, stderr=PIPE,
          universal_newlines=True)
out, err = p.communicate(sudo_password + "\n")
print out.strip("None")