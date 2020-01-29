# Communicator

Telegram bot for interaction with clients.

# Questionary

Questions are stored in files with name pattern: `<name>_model.ini`

`<name>`, is a questionary name.

Once new questionary file is created it should be added to `settings.ini`:

* `CATEGORIES`, is responsible for display name. List questionary names here. 
Items from this list will display as menu items right after welcome message.
* `MODELS`, is responsible for file name. List Qustionary model names here.
Bot will look for file names from this list.

Both lists (`CATEGORIES`, `MODELS`) should have the same number is items and
 items order in `CATEGORIES` list should respect to items order in `MODELS` 
list.

## Create new questions model file

## Fill generic section in file <name>_model.ini
## Fill questions in file <name>_model.ini
```
[<Question ID>]
question=<Write your question here....>
answer=< RegEx to verify the answer>
next_question=<Qustion ID1>
```

