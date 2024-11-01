echo "Starting Gunicorn server..."
gunicorn app:app &

echo "starting VideoConvertor ~@Dronebots";
python3 bot.py
