from dotenv import load_dotenv

from archivy import app as application


def run():
    print("Running archivy.wsgi")
    load_dotenv()

    application.run()


if __name__ == "__main__":
    run()
