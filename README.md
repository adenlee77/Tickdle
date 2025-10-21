** TICKDLE **

This is a guessing game with a new ticker symbol every day. It gives you a candlestick chart and you guess which stock it is. Higher or lower stats are given on every guess.  

To run locally
1. start the flask server in the backend directory by running "flask run"
2. start the redis cache with "docker run -d --name redis-cache -p 6379:6379 redis:7-alpine" (make sure you have docker running on your local computer)
3. start the frontend in the frontend directory with "npm run dev"