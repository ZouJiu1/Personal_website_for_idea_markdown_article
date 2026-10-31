"""项目路径工具：自动确定项目根目录，避免硬编码绝对路径。

项目根目录 = mysite 包所在目录的上一级（即仓库根目录）。
所有数据目录（article、people、hls 等）都相对于该根目录定位。
"""
import os

# 项目根目录（自动确定，无需指定）
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def project_path(*parts):
    """返回项目根目录下的绝对路径。"""
    return os.path.join(PROJECT_ROOT, *parts)


def web_relative_path(abspath):
    """把项目内的绝对路径转换为站点相对路径（以 / 开头）。

    若路径不在项目根目录内则原样返回，交由调用方兼容处理。
    处于 dist/ 下的路径会剥掉 dist 前缀（nginx 中 /article、/people 指到项目根）。
    """
    try:
        rel = os.path.relpath(abspath, PROJECT_ROOT)
    except (ValueError, TypeError):
        return abspath
    if rel.startswith(".."):
        return abspath
    rel = rel.replace(os.sep, "/")
    if rel.startswith("dist/"):
        rel = rel[len("dist/"):]
    return "/" + rel


def web_dir_of(filepath):
    """返回文件所在目录的站点相对路径（用于拼接 <img src> 等）。"""
    dirabs = os.path.dirname(filepath)
    webdir = web_relative_path(dirabs)
    if webdir == dirabs and "vue-project" in filepath:
        # 兼容旧部署目录名
        idx = filepath.index("vue-project") + (16 if "dist" in filepath else 11)
        webdir = filepath[idx:len(dirabs)]
    return webdir


# 置顶标记文件名：think 模块历史上用 TOP.text，csdn/markdown_detail 模块用 TOP.txt。
# 读操作兼容两种命名，写操作统一为各自模块的标准命名。
TOP_THINK = "TOP.text"
TOP_CSDN = "TOP.txt"


def find_top_marker(dirpath, standard):
    """返回目录下实际存在的置顶标记文件路径（兼容 TOP.text / TOP.txt 两种历史命名）。

    两种命名都不存在时返回标准命名的路径，供调用方做写入/存在性判断。
    """
    alt = TOP_CSDN if standard == TOP_THINK else TOP_THINK
    for name in (standard, alt):
        p = os.path.join(dirpath, name)
        if os.path.exists(p):
            return p
    return os.path.join(dirpath, standard)
