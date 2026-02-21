import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from app import create_app

app = create_app()

def main():
    print("Starting PathPilot Flask server...")
    app.run(debug=True, port=5000, host='0.0.0.0')

if __name__ == "__main__":
    main()