# Welcome to Simple Chat  
Welcome to Simple Chat, a real-time chat application that leverages the power of Python, Django, and Redis. The application facilitates real-time communication between authenticated users, making use of WebSockets for instant message delivery.
## Key Features
* **Real-time Communication:** Utilizes WebSockets for real-time, bi-directional communication between users.
* **User Management:** Supports user registration and authentication. User data is stored and managed using a relational database (PostgreSQL or MySQL).
* **Redis Storage:** For rapid message delivery, the most recent messages (default 100) are stored in Redis, an in-memory data store known for its performance.
* **Persistent Storage in Database:** Although Redis is highly efficient and quick, it is not built to sustain millions of messages from a vast user base. For long-term storage or when a user needs to access older messages that go beyond the most recent ones, the application switches to retrieving the messages from the database. This system ensures that Redis doesn't get overwhelmed, maintaining optimal performance.
* **Message Throttling:** To prevent spamming and maintain the quality of the chat experience, the application implements API throttling for messages in real time. The current rate limit is 1 message per 2 seconds (configurable).
* **Logging:** The application maintains detailed logs of activity and unexpected errors using two models: `Generic_Activity_Log` and `Generic_Error_Log`. This aids in monitoring user activity and troubleshooting issues.
* **Monitoring:** The application uses Prometheus for monitoring, providing insights into its performance and usage.
* **Asynchronous Tasks with Celery:** Some tasks, such as logging and storing messages to the database, are performed asynchronously using Celery. This ensures that these operations don't block the main application flow, thus enhancing the user experience and application performance. It also decouples the task execution from the WebSocket communication, allowing the application to scale better.
* **Signup Data and Form Validation:** the application uses Django's built-in forms for user registration. This includes fields for name, last name, and email. Django automatically validates these fields to ensure they are not empty and that the email is in the correct format.

## API and JSON structure
Users connect to WebSocket via `ws/userchat/{conversation_id}/`
This endpoint is secured to ensure only participants of the `conversation`can access it.

Message structure is simplistic:
```javascript
{  
    "message": "string",  // The message text.  
    "sender": "integer",  // The ID of the user who sent the message. Which is populated by the backend.
    "timestamp": "string" // The time the message was sent, in the format 'YYYY-MM-DD HH:MM:SS'. Also populated by the backend
}  
```
This structure allows for clear and concise communication of data between the client and server.
## Setup  
  
To get started, follow the steps below:  
  
1. Create a virtual environment.  
2. Install the project dependencies with `pip install -r requirements.txt`.  

Note: Docker instructions bellow
  
## Running the Application  
  
To run the server, use the following command:
```bash  
uvicorn SimpleChatRooms.asgi:application  
```
To run the Celery task server, use the following command:
```bash  
celery -A SimpleChatRooms worker -P threads --concurrency=1 --loglevel=info  
 ```
Note: The Celery task server is not required for the project to run - however logging and fetching older messages wont work properly. And not running it might involve commenting the task triggers to keep functionality.

If you're using PostgreSQL, you can increase concurrency.


## Deployment & Docker 
  
You can check out the live deployment of this project on an Azure VM at: [https://sograpp.com](https://sograpp.com) (this was just a domain i had unused) 

To deploy this with docker you must:
1. Clone this git
2. Run `docker-compose build`
3. Run `docker-compose up`
4. (optional) create a superuser run `sudo docker exec -it {container_id} python manage.py createsuperuser` (find the container id for the container with the name ending in **web** via `docker ps`)

The Server should live on port 8000 (edit yml file to change)

Note: A few more steps are required to deploy the container on a server - such as setting up Nginx/apache, handling SSL...

## Frontend notes
  
Several external libraries were used for the frontend:  
  
- Select2 for enhanced selections.  
- Bootstrap for simplified and attractive frontend styling.  
- jQuery to simplify the code.  
  
Design references for the login, register, profile, and chat pages are as follows:  
  
- Login/Register/Profile: [CodePen Link](https://codepen.io/scanfcode/pen/jGeezR)  
- Chat: [BBBootstrap Link](https://bbbootstrap.com/snippets/simple-chat-application-57631463)  

## Running the tests
To run the test extra packages must be installed:
`
pytest
daphne
pytest-asyncio
`
These are necessary to test the Websockets.

after installing these packages run:
```bash
python manage.py test messaging.tests.http_tests
```
and
```bash
pytest messaging/tests/websocket_tests.py
```
