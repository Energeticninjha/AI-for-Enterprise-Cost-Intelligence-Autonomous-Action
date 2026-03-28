import pytest
import sys

def main():
    exit_code = pytest.main(['-v', 'test_self_healing.py'])
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
