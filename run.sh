npx tailwindcss -i ./tracker_rhizome_dev/app/css/main.css -o ./tracker_rhizome_dev/app/static/style.css --minify --watch &
uvicorn tracker_rhizome_dev.app.main:app --reload --workers 8 --port 8001
