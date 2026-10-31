import hashlib
import os
import sys
import argparse

# 与 mysite/csdn/views.py 保持一致：
# member.txt 第一字段只存「加盐格式」sha256s$<salt>$<digest>，
# digest = sha256(salt + 前端 sha256 值)。旧格式（裸 sha256）已彻底弃用，
# 本脚本输出的即是可直接替换 member.txt 对应用户行第一字段的加盐格式。
SALT_PREFIX = "sha256s$"


def genpassword(password):
    """前端登录传输/存储基准的 sha256 十六进制值。"""
    key = bytes(password, encoding='utf-8')
    sha = hashlib.sha256()
    sha.update(key)
    return sha.hexdigest()


def salted_from_value(value):
    """把 sha256 值转为加盐存储格式 sha256s$<salt>$<digest>。"""
    salt = hashlib.sha256(os.urandom(32)).hexdigest()[:32]
    digest = hashlib.sha256((salt + value).encode('utf-8')).hexdigest()
    return SALT_PREFIX + salt + "$" + digest


if __name__ == "__main__":
    # 用法：python3 genpassword.py [--pw 新密码]
    #   --pw  指定新密码；缺省使用脚本内默认密码
    parser = argparse.ArgumentParser()
    parser.add_argument('--pw', type=str, default='')
    args = parser.parse_args()

    password = args.pw or '12ab[,'
    if len(password) == 0:
        raise RuntimeError(password)

    ret = salted_from_value(genpassword(password))

    with open('genpassword', 'w') as obj:
        obj.write(password + "\n" + ret)
    print(ret)
