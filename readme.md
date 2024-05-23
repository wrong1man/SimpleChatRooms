# Welcome to Simple Chat  
  
Simple Chat is a project that demonstrates the use of websockets to create real-time communication between authenticated users.  
  
## Setup  
  
To get started, follow the steps below:  
  
1. Create a virtual environment.  
2. Install the project dependencies with `pip install -r requirements.txt`.  
  
## Running the Server  
  
To run the server, use the following command:   
  
```bash  
uvicorn SimpleChatRooms.asgi:application  
```
After running the server, you can register and log in to the application.

## Features

From the profile page, you can initiate chats with any existing user or continue a previous chat. Note that you can only have one chat per user. If you attempt to start a new chat with the same user, the existing chat will be opened.

Redis is used to store the last 100 messages. Due to the potential for high memory usage and data loss with Redis, Celery tasks have been implemented with RabbitMQ to run separately and asynchronously from the websockets and the regular backend. These tasks add messages to the database, allowing for message retrieval in case Redis fails or when you want to access more than the last 100 messages.

To run the Celery task server, use the following command:
```bash  
celery -A SimpleChatRooms worker -P threads --concurrency=1 --loglevel=info  
 ```
Note: The Celery task server is not required for the project to run.

If you're using PostgreSQL, you can increase concurrency.

It is possible to store more messages with Redis with some simple edits.

### Logging
Loging is done on a database level. It is simpler and allows for easy access and filtering.
`Generic_Activity_Log` holds activity logs for logged in users (log in, open chat, send message, etc).
`Generic_Error_Log` holds logs for unexpected errors in execution.

## Database  
  
SQLite was used during development, whereas PostgreSQL is used with Docker for live deployment.  
  
## Deployment  
  
You can check out the live deployment of this project on an Azure VM at: [http://***](http://***)  
  
## Frontend  
  
Several external libraries were used for the frontend:  
  
- Select2 for enhanced selections.  
- Bootstrap for simplified and attractive frontend styling.  
- jQuery to simplify the code.  
  
Design references for the login, register, profile, and chat pages are as follows:  
  
- Login/Register/Profile: [CodePen Link](https://codepen.io/scanfcode/pen/jGeezR)  
- Chat: [BBBootstrap Link](https://bbbootstrap.com/snippets/simple-chat-application-57631463)  
