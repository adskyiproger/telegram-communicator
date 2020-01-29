# Communicator

Telegram bot for client dialogs support.

# Questionary

## Create new questions model file

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

Questionary configuration file has sections:

* generic, section that contains questionary configuration like name, greeting message, bye message.
* the rest of the file content are question sections

## Fill generic section in file <name>_model.ini

Generic section format:
```
[generic]
name=<some text here>
last_message=<some test here>
```

Generic section has following properties:

* `name`, Questionary name and may contain some description
* `last_message`, Message to display once questionary is completed

## Fill questions in file <name>_model.ini

Qustion section format:

```
[<Question ID>]
question=<Write your question here....>
answer=< RegEx to verify the answer>
next_question=<Qustion ID1>
```

Question section has following properties:

* `question`, Text of the question
* `answer`, acceptable RegEx for answer. E/g: phone number may contain only
 digits. This field may contain acceptable list of answers. E/g: Yes|No.
* `next_question`, name of the next question section. If `answer` field has
a list of possible answers then this section should also contain a list if
possible next questions. E/g: if `answer=Yes|No` then `next_question=q4|finish`.
`finish` is a special keyword to identify the end of the questionary.
