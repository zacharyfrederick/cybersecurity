from app import app
import sys

if __name__ == '__main__':
    if sys.platform == 'darwin':
        app.run()
    else:
        app.run(host='0.0.0.0', port=80)
