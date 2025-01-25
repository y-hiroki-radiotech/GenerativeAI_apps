import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--text", default="xxx")
    args = parser.parse_args()
    print(args.text)
