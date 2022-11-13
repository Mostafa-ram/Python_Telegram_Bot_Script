import configparser
from sqlite3 import Date
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

### Initializing Configuration.

print("Initializing configuration...")
config = configparser.ConfigParser()
config.read('config.ini')

### Read values for Telethon and set session name from config file.

API_ID = config.get('default', 'api_id')
API_HASH = config.get('default', 'api_hash')
BOT_TOKEN = config.get('default', 'bot_token')
session_name = "My_bot"

### Read database credentials from config file.

USERNAME = config.get('default', 'username')
PASSWORD = config.get('default', 'password')
DATABASE_NAME = config.get('default', "db_name")
COLLECTION_NAME = config.get('default', "collection_name")

# Start the Client (telethon).....
client = TelegramClient(session_name, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Start the Client (MongoDB).....
url = "mongodb+srv://" + USERNAME + ":" + PASSWORD + "@clusterbot.qj7fnmy.mongodb.net/?retryWrites=true&w=majority"
cluster = MongoClient(url)


                                 #### End Of Configuration Part ####
                              #### ٍStart of Bot functions Part Part ####


### Bot has (5) Commands [/start, /insert, /select, /update, /delete]
### every command has its own function at following lines

# (Print function) that converting data that comes from database from object to array.
def convert_from_obj_to_list(returned_data):
    text = ""
    for res in returned_data:
        if (res != []):
            id = res["id"]
            name = res["name"]
            password = res["password"]
            created_date = res["created_date"]
            text = [id, name, password, created_date]
    message = text
    return message


### 1- START COMMAND.
@client.on(events.NewMessage(pattern="(?i)/start"))
async def start(event):
    # Get users Name >>
    sender = await event.get_sender()
    SENDER = sender.id
    sen = sender.first_name
    # print(sen)
    # print(sen)

    # searching for the user in database >>
    results = password_manager_app.find({"name": sen})
    text = convert_from_obj_to_list(results)

    # this part Do 2 things >>
    # first thing .. check the expiration of users information (informations expire after just 1 min for easy test).
    # second thing .. trying to identify the user by searching for the username in database.
    if (len(text) >= 2):
        print("old_time:")
        print(text[3])
        currentTime = datetime.now().strftime("%M")
        print("Current_time:")
        print(currentTime)
        a = text[3]
        b = currentTime
        # returns a timedelta object
        c = int(b) - int(a)
        print('Difference: ', c)

        if str(text[1]) == str(sen):
            if c > 1:
                await client.send_message(SENDER, "your info is expired .. update it...")
            else:
                await client.send_message(SENDER, "welcome back i know you...")
        else:
            await client.send_message(SENDER, "i dont know you .. please enter your info...")
    else:
        await client.send_message(SENDER, "i dont know you .. please enter your info...")

    # print("there is user pressed /start and his name is " + sender.first_name)


### 2- Insert command.
# /insert [id] [name] [password]
@client.on(events.NewMessage(pattern="(?i)/insert"))
async def insert(event):
    # Get the sender of the message
    sender = await event.get_sender()
    SENDER = sender.id

    # Split the inserted text and create a List.
    list_of_words = event.message.text.split(" ")

    id = int(list_of_words[1])
    name = list_of_words[2]
    password = list_of_words[3]
    currentDT = datetime.now().strftime("%M")

    post_dict = {"id": id, "name": name, "password": password, "created_date": currentDT}

    # Execute insert query.
    password_manager_app.insert_one(post_dict)

    # send notification message.
    text = "user info correctly inserted!"
    await client.send_message(SENDER, text, parse_mode='html')


### (Print function for SELECT COMMAND).
# (Print function) that converting data that comes from database from object to html DOC/(readable text).
def create_message_select_query(ans):
    text = ""
    for res in ans:
        if (res != []):
            id = res["_id"]
            name = res["name"]
            password = res["password"]
            created_date = res["created_date"]

            text += "<b>" + str(id) + "</b> | " + "<b>" + str(name) + "</b> | " + "<b>" + str(
                password) + "</b> | " + "<b>" + str(created_date) + "</b> "

    message = "<b>Received  </b> Information about users:\n\n" + text
    return message


### 3- SELECT COMMAND.
@client.on(events.NewMessage(pattern="(?i)/select"))
async def select(event):
    # Get the sender of the message.
    sender = await event.get_sender()
    SENDER = sender.id

    # Split the inserted text and create a List.
    list_of_words = event.message.text.split(" ")

    # select exact user info by _id if it exests.
    if (len(list_of_words) > 1):
        name = list_of_words[1]
        # Execute find query.
        results = password_manager_app.find({"name": name})
        # send notification message..
        text = create_message_select_query(results)
        await client.send_message(SENDER, text, parse_mode='html')

    # select all if the user did not insert any _id..
    else:
        # Execute find query.
        results = password_manager_app.find({})
        # send notification message..
        text = create_message_select_query(results)
        await client.send_message(SENDER, text, parse_mode='html')


### 4- UPDATE COMMAND.
# /update [_id] [new_name] [new_password]
@client.on(events.NewMessage(pattern="(?i)/update"))
async def update(event):
    # Get the sender
    sender = await event.get_sender()
    SENDER = sender.id
    # Split the inserted text and create a List.
    list_of_words = event.message.text.split(" ")

    # print("Updattttt")
    # print(list_of_words)
    currentDT = datetime.now().strftime("%M")

    id = ObjectId(list_of_words[1])
    name = list_of_words[2]
    password = int(list_of_words[3])
    new_post_dict = {"name": name, "password": password, "created_date": currentDT}

    # Execute update query
    password_manager_app.update_one({"_id": id}, {"$set": new_post_dict})

    # send notification message
    text = "user with _id {} correctly updated".format(id)
    await client.send_message(SENDER, text, parse_mode='html')


### 5- DELETE COMMAND.
# /delete [_id]
@client.on(events.NewMessage(pattern="(?i)/delete"))
async def delete(event):
    # Get the sender(user)
    sender = await event.get_sender()
    SENDER = sender.id

    # Split the inserted text and create a List.
    list_of_words = event.message.text.split(" ")
    _id = ObjectId(list_of_words[1])

    # Execute delete query.
    password_manager_app.delete_one({"_id": _id})

    # send notification message.
    text = "user with _id {} correctly deleted".format(_id)
    await client.send_message(SENDER, text, parse_mode='html')


##### main #####
if __name__ == '__main__':
    try:
        print("Initializing Database...")
        # Define the Database using Database name.
        db = cluster[DATABASE_NAME]
        # Define collection
        password_manager_app = db[COLLECTION_NAME]

        print("Bot Started...")
        client.run_until_disconnected()

    except Exception as error:
        print('Cause: {}'.format(error))