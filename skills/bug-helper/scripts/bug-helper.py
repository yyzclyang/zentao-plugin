#!/usr/bin/env python3
"""禅道 API 脚本，支持 bug-list / bug-detail 子命令。"""

import json, os, re, sys, tempfile, urllib.request, urllib.error

def load_env():
    """加载 .env 文件到环境变量。"""
    env_path = os.path.join(os.getcwd(), ".env")
    if not os.path.isfile(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

def require_env(*names):
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        print(f"错误：缺少环境变量: {' '.join(missing)}", file=sys.stderr)
        sys.exit(1)

def api_get(path):
    """请求禅道 API，返回解析后的 JSON。"""
    url = f"{os.environ['ZENTAO_URL']}/api.php/v1{path}"
    req = urllib.request.Request(url, headers={"Token": os.environ["ZENTAO_TOKEN"]})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

def download_image(file_id, bug_id):
    """下载禅道附件图片到 /tmp，返回本地路径。"""
    url = f"{os.environ['ZENTAO_URL']}/file-read-{file_id}.png"
    path = os.path.join(tempfile.gettempdir(), f"zentao_bug_{bug_id}_img_{file_id}.png")
    urllib.request.urlretrieve(url, path)
    return path

# ── 子命令 ──────────────────────────────────────────────

def cmd_bug_list(args):
    require_env("ZENTAO_URL", "ZENTAO_TOKEN", "ZENTAO_PRODUCT_ID")
    limit = int(args[0]) if args else 20
    data = api_get(f"/products/{os.environ['ZENTAO_PRODUCT_ID']}/bugs?status=assigntome&limit={limit}")
    print(json.dumps(data, ensure_ascii=False))

def cmd_bug_detail(args):
    require_env("ZENTAO_URL", "ZENTAO_TOKEN")
    if not args:
        print("用法: zentao.py bug-detail <bug-id>", file=sys.stderr)
        sys.exit(1)
    bug_id = args[0]
    data = api_get(f"/bugs/{bug_id}")
    # 提取 steps 中的图片 file-id，自动下载
    steps = data.get("steps", "")
    images = []
    for fid in set(re.findall(r"file-read-(\d+)", steps)):
        path = download_image(fid, bug_id)
        images.append({"file_id": fid, "path": path})
    if images:
        data["_images"] = images
    print(json.dumps(data, ensure_ascii=False))

# ── 入口 ────────────────────────────────────────────────

COMMANDS = {
    "bug-list": cmd_bug_list,
    "bug-detail": cmd_bug_detail,
}

def main():
    load_env()
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"用法: zentao.py <{'|'.join(COMMANDS)}> [args...]", file=sys.stderr)
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])

if __name__ == "__main__":
    main()
