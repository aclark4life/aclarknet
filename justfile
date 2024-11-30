default:
    echo 'Hello, world!'

pip-install:
    pip install -e .
alias i := pip-install

open:
    open http://localhost:8000
alias o := open
