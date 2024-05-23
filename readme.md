#Welcome to Simple Chat.
This project shows how to use websockets to allow authenticated users to send messages to each other.

To setup, create a virtual envirenment and run:
`pip install -r requiremenmts.txt`

To run the server use:
`uvicorn SimpleChatRooms.asgi:application`
You can then login and register.

from the `profile` page you can start chats with any existing user, or pickup and old chat. You can only have one chat for each user; Attempting to start a new chat with the same user will open the old chat.

Redis will hold the last 100 messages sent as it can become very memory heavy, and there's a risk of data loss.
Because of this, i've added some celery tasks with rabitmqq that will run seperately and async from the websockets and the regular backend.
This celery task adds messages to the database, allowing for retrieval if the redis fails or you want more than the last 100 messages.
I believe this is the proper way to execute the task.
The celery task server does not need to be running for the project to run. you can run it with:
`celery -A SimpleChatRooms worker -P threads --concurrency=1 --loglevel=info`
If you elect to go with the postgresql route you can increase concurrency.

##Database
SQL Database. sqlite used during development; postgresql used with docker/live deployment.

You can check the deployment of this project (deployed on a Azure VM) at: http://***

For the front-end some corners were cut.

##Frontend:
External libraries used:
select2 - better selections.
bootstrap - simplify css to beautify frontend a little.
Jquery - simplify some code.

Design:
Login/register/profile: https://codepen.io/scanfcode/pen/jGeezR
Chat: https://bbbootstrap.com/snippets/simple-chat-application-57631463

