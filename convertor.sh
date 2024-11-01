echo "Starting Gunicorn server..."
gunicorn app:app &

echo "starting V-OPZ ~@RVX...";
python3 bot.py
