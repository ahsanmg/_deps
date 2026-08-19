import os
import shutil
import sys
import tarfile
from pathlib import Path
from argparse import ArgumentParser

def copy_libraries(target_bin_dir: Path, package_dir: Path):
    target_bin_dir.mkdir(parents=True, exist_ok=True)

    if sys.platform == "win32":
        library_suffixes = (".dll",)
        platform_name = "windows"
    elif sys.platform == "linux":
        library_suffixes = (".so",)
        platform_name = "linux"
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")

    for source in package_dir.rglob("*"):
        if not source.is_file():
            continue

        # Linux libraries can be named:
        #   libfoo.so
        #   libfoo.so.2500
        # so check for ".so" anywhere in the suffix.
        if sys.platform == "linux":
            is_library = ".so" in source.name
        else:
            is_library = source.suffix.lower() in library_suffixes

        if not is_library:
            continue

        destination = target_bin_dir / source.name

        if not destination.exists():
            shutil.copy2(source, destination)
            print(f"Copied: {source.name}")



if __name__ == "__main__":
    parser = ArgumentParser(description="Packages archive.")

    parser.add_argument("--bin_dir", required=True, type=Path, help="Binary directory to copy library files (e.g. dlls, .so) to")
    parser.add_argument("--pkg_dir", required=True, type=Path, help="Root directory to scan for library files (e.g. dlls, .so) for")
    args = parser.parse_args()

    pkg_dir = Path(args.pkg_dir)
    target_bin_dir = Path(args.bin_dir)
    copy_libraries(target_bin_dir, pkg_dir)