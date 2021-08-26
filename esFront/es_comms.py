import paramiko
import time

# DONT UPLOAD usrpass.txt TO GIT
creds = []
with open('usrpass.txt') as f:
    for line in f:
        creds.append(line.strip())

server = creds[0]
username = creds[1]
password = creds[2]

def ESsearch(searchtext):
    ssh = paramiko.SSHClient()
    query = """{\\"from\\" : 0, \\"size\\" : 10,\\"query\\": {\\"multi_match\\" : {\\"query\\": \\" """.strip() + searchtext + """\\",\\"fields\\": [ \\"title\\",\\"description\\",\\"developer\\"]}}} """


    write_query = f"""echo {query} > qfile.json"""
    pritq = """cat qfile.json"""
    es_query = """curl -K auth.conf -XGET "https://tux-es1.cci.drexel.edu:9200/av667_info624_202004_project_no_doc_prefix/_search" -H 'Content-Type: application/json' -d@qfile.json -k"""


    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=username, password=password)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(write_query)
    #print(str(ssh_stdout.read()))
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(es_query)
    results = str(ssh_stdout.read())
    #ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(pritq)
    #print(str(ssh_stdout.read()))

    #time.sleep(.05)
    ssh.close()
    return results

#print(ESsearch("super mario bros 3"))