import sys
import hashlib
import tarfile
import zipfile
import urllib.request
from pathlib import Path
from argparse import ArgumentParser

import hashlib
import tarfile
import urllib.request
from pathlib import Path

def _download(url: str, destination: str):
    def reporthook(block_num, block_size, total_size):
        downloaded = block_num * block_size

        if total_size > 0:
            percent = min(downloaded / total_size * 100, 100)
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)

            print(
                f"\rDownloading {destination}: "
                f"{percent:6.2f}% "
                f"({downloaded_mb:.1f}/{total_mb:.1f} MB)",
                end="",
                flush=True,
            )
        else:
            downloaded_mb = downloaded / (1024 * 1024)
            print(
                f"\rDownloading {destination}: "
                f"{downloaded_mb:.1f} MB",
                end="",
                flush=True,
            )

    print(f"Downloading {url}")
    urllib.request.urlretrieve(url, destination, reporthook=reporthook)
    print()


def _sha256(path: Path) -> str:
    size = path.stat().st_size
    processed = 0
    sha256 = hashlib.sha256()

    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            sha256.update(chunk)
            processed += len(chunk)

            percent = processed / size * 100
            print(
                f"\rCalculating SHA256: {percent:6.2f}%",
                end="",
                flush=True,
            )

    print()
    return sha256.hexdigest().lower()


def extract_archive(archive: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting {archive}...")

    if archive.suffix.lower() == ".zip":
        with zipfile.ZipFile(archive, "r") as z:
            members = z.infolist()
            total = len(members)

            for index, member in enumerate(members, 1):
                parts = Path(member.filename).parts

                if len(parts) <= 1:
                    continue

                # Strip first directory component.
                relative_path = Path(*parts[1:])

                target = output_dir / relative_path

                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)

                    with z.open(member) as src, target.open("wb") as dst:
                        dst.write(src.read())

                percent = index / total * 100
                print(
                    f"\rExtracting: {percent:6.2f}% "
                    f"({index}/{total})",
                    end="",
                    flush=True,
                )

    elif archive.name.lower().endswith((".tar.gz", ".tgz")):
        with tarfile.open(archive, "r:gz") as tar:
            members = tar.getmembers()
            total = len(members)

            for index, member in enumerate(members, 1):
                parts = Path(member.name).parts

                if len(parts) <= 1:
                    continue

                member.name = str(Path(*parts[1:]))
                tar.extract(member, output_dir)

                percent = index / total * 100
                print(
                    f"\rExtracting: {percent:6.2f}% "
                    f"({index}/{total})",
                    end="",
                    flush=True,
                )

    else:
        raise ValueError(f"Unsupported archive format: {archive}")

    print()
    print(f"Extracted {archive} to {output_dir}")


def get_openvino(
    base: str,
    archive: str,
    sha_file: str,
    output_dir: Path,
):
    archive_path = Path(archive)
    sha_path = Path(sha_file)
    output_dir = Path(output_dir)

    # Download archive
    _download(
        f"{base}/{archive}",
        str(archive_path),
    )

    # Download SHA256 file
    _download(
        f"{base}/{sha_file}",
        str(sha_path),
    )

    # Verify SHA256
    print(f"Verifying {archive}...")

    actual = _sha256(archive_path)
    expected = sha_path.read_text().strip().split()[0].lower()

    if actual != expected:
        raise RuntimeError(
            f"OpenVINO SHA256 mismatch: "
            f"expected {expected}, got {actual}"
        )

    print(f"OpenVINO SHA256 verified: {actual}")

    # Extract
    extract_archive(archive_path, output_dir)


if __name__ == "__main__":
    parser = ArgumentParser(description="Downloads and extracts OpenVINO archive.")

    parser.add_argument("--ov_base", required=True, help="Provide the base of the platform specific OpenVINO archive")
    parser.add_argument("--ov_archive", required=True, help="Full archive name with extension")
    parser.add_argument("--ov_dir", required=True, type=Path, help="OpenVINO extraction output directory")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()

    # Download openvino
    ov_base = args.ov_base
    ov_archive = args.ov_archive
    sha_file = f"{ov_archive}.sha256"
    output_dir = args.ov_dir
    get_openvino(ov_base, ov_archive, sha_file, output_dir)