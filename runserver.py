import waitress
from DocProbAssist.wsgi import application

if __name__ == "__main__":
    print("server")
    waitress.serve(application, port=8000, threads=4, host="0.0.0.0")
