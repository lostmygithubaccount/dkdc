def main(file, testcase, result):
    code = "import pytest\ndef {}():\n    assert '{}'=='ok'".format(testcase, result)
    with open(file, "w+") as f:
        f.write(code)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate test result')
    parser.add_argument('--file', default=None)
    parser.add_argument('--result', default=None)
    parser.add_argument('--testcase', default=None)

    args = parser.parse_args()
    print(args)

    main(args.file, args.testcase, args.result)
