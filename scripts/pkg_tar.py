import argparse
import os
import tarfile

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="Source directory")
    parser.add_argument("out", help="Output .tar.gz file")
    args = parser.parse_args()

    with tarfile.open(args.out, "w:gz") as tar:
        for name in os.listdir(args.src):
            tar.add(os.path.join(args.src, name), arcname=name)


if __name__ == "__main__":
    main()
