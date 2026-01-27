FOOD ORDER & DELIVERY

1. Data models
   - menu items(id, name, description, price)
   - orders(id, items, customer info, order status, placed_at, eta_delivery)

2. Flask API Endpoints
   - GET /menu            # view menu
   - POST /order          # place an order (returns ETA)
   - GET /order/<id>      # view order status and remaining delivery time

3. Order Creation
   - POST /order:
      - accept item selections (optional get customer info like name, adress)
      - set random ETA between 5 minutes and 1 hour (since it's just for show, also possible to make it that we have a central dot on google maps and then we measure from the written adress + time it takes to make the food)
      - store order with timestamp and ETA into psql database
      - return order id, ETA, and details (so that it has like a timer in the middle of the page and details about the order up)

4. Order Status Tracking
   - GET /order/<id>:
      - remaining delivery time (or delivered, we do that by taking the timestamp, the eta and then checking what time it is now, then take the time left and write it out, for the sake of a timer we can just make the timer go on from the load so there isn't a call every second)
      - return order status, ETA (calc. eta), and time left/completed 

5. Data Persistence
   - start -> in-memory storage (dictionary)
   - optional! psql database for the data to stay (would be good since i think we need to have more parts of the app, also the menu can then be changed)

6. Docker & Requirements
   - as stuff changes we add it to requirements.txt and update the docker files

7. Kubernetes (k8s)
   - updating deployment and exposing new endpoints (if we need to)

OPTIONAL ADDITIONS:
- adding a business side which can change the menu and accept or refuse delivery (this would mean that then there's a timestamp and a accepted timestamp)
- if we choose to add accept or refuse delivery we can add "food being made" and then out for delivery after a set time