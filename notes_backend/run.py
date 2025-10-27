from app import app

if __name__ == "__main__":
    # Do not bind port explicitly; respect environment/preview configuration.
    app.run()
