from app import app
import sys

if __name__ == '__main__':
    if sys.platform == 'darwin':
        app.run()
    else:
        app.run(host='', port=5000)
