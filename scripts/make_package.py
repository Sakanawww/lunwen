"""把项目打包为可直接发给老师的离线 zip（同时保持 GitHub 仓库可直接 clone 部署）。

排除开发/运行时内容：.git、.venv、node_modules、缓存、日志、密钥、
运行时数据（上传文件/向量索引）与个人论文材料。

用法：.venv/Scripts/python.exe scripts/make_package.py
输出：项目上级目录下 课程助教系统-交付包-<日期>.zip
"""
import os
import zipfile
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".mimosa", ".agents", ".claude", ".idea", ".vscode",
    "论文", "模板", "dist", ".pids", ".logs",
}
EXCLUDE_FILES = {".env", ".fernet_key", "scratch_seed_test.py"}
EXCLUDE_SUFFIXES = {".log", ".pyc"}


def included(path: Path) -> bool:
    rel = path.relative_to(BASE)
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return False
    if path.name in EXCLUDE_FILES:
        return False
    return path.suffix.lower() not in EXCLUDE_SUFFIXES


def main() -> None:
    out = BASE.parent / f"课程助教系统-交付包-{date.today():%Y%m%d}.zip"
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(BASE.rglob("*")):
            if not path.is_file() or not included(path):
                continue
            zf.write(path, Path("course-ta") / path.relative_to(BASE))
            n += 1
    size_mb = out.stat().st_size / 1024 / 1024
    print(f"已生成 {out.name}（{n} 个文件，{size_mb:.1f} MB）")
    print("老师拿到后：解压 → 按 README「快速部署」四步执行即可。")


if __name__ == "__main__":
    main()
