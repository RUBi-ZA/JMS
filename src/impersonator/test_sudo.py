from subprocess import Popen, PIPE
import getpass, sys

sudo_password = sys.argv[1]

p = Popen("su - rubi -c 'qstat -x'", shell=True, stdin=PIPE, stderr=PIPE,
          universal_newlines=True)
out, err = p.communicate(sudo_password + "\n")

print out
print err

#print out.strip("None")
