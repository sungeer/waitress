# waitress

*An agent built with LangGraph.*

## Installation

clone:
```
$ git clone git@github.com:sungeer/waitress.git
$ cd waitress
```
create & activate virtual env then install dependency:

with venv/virtualenv + pip:
```
$ python -m venv env  # use `python3 ...` for Python3 on Linux & macOS
$ source env/bin/activate  # use `env\Scripts\activate` on Windows
$ pip install -r requirements.txt
```
then run:
```
$ uvicorn waitress:app --port 8848
* Running on http://127.0.0.1:8848/
```

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).
