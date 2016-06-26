"""
Lambdapager cli entrypoint
"""
from lambdapager import LambdaPager

def main():
    lp = LambdaPager()
    lp.run()

if __name__ == '__main__':
    main()
