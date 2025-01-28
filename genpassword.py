import hashlib
import sys
import argparse

def genpassword(password):
    key = bytes(password, encoding='utf-8')
    sha = hashlib.sha256()
    sha.update(key)
    ret = sha.hexdigest()
    return ret

if __name__=="__main__":
    # pd = '01ab!+'
    # argv = sys.argv
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--pw', type=str, default = "")
    # args = parser.parse_args()

    password = '06hj@#'
    if len(password)==0:
        raise RuntimeError(password)
    
    ret = genpassword(password)
    
    with open('genpassword', 'w') as obj:
        obj.write(password + "\n" + ret)