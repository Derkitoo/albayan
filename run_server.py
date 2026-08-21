import sys
import os

# Set UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    print("==========================================================")
    print("Démarrage du prototype Sunnah.com Sharh AI Assistant")
    print("Interface Web : http://localhost:8000")
    print("API Docs      : http://localhost:8000/docs")
    print("==========================================================")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
