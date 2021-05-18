#Personal Budget

##Use

###Initial Set Up
Create a SQLite database on your local machine - preferrably outside this directory so that it will be less likely you push it to GitHub - by doing the following:

1) `cd` to the directory you want to create the SQLite database.
2) Run `sudo apt install sqlite3` (assuming your machine uses `apt`).
3) Run `sqlite3 budget` to create the `budget` database and enter the `sqlite3` program.
4) Run `.read <path to personal-budget>/personal-budget/personal_budget/data/schema.sql`.  For example, `.read /home/pc/repos/personal-budget/personal_budget/data/schema.sql`.  To create the database schema based on the `/personal_budget/data/schema.sql` in this repo.
5) Run `.tables` to confirm that all 3 tables have been created (the output of this command should list `category`, `transactions_categories`, and `transactions`).
6) Run `.exit` to exit the SQLite program.

Create a `config.json` file on your local machine - again referrably outside this directory so that it will be less likely you push it to GitHub - by doing the following steps.  This file will be passed into the `personal-budget` Python script to give it context on what financial institution to get data from, how many days to get data for, and where the SQLite database is to store the transactions it retrieves.

1) Create a file named `config.json` on your local machine.
2) Open the file in a text editor like `vim`, `Notepad`, or `Sublime`.
3) Copy and paste the following into the file:

```
{
    "institution_name": "<your financial institution name>",
    "member_id": "<your member id>",
    "password": "<your password>",
    "number_of_transaction_days": "30",
    "sqlite_db_file_path": "<the absolute path to the SQLite database you created above>"
}
```

###Regular Use
To run the `personal-budget` script, do the following steps:

1) `cd` to the `personal-budget` directory if you're not already there.
2) Run `python3 ./personal_budget/main.py <absolute path to your config.json here>`.  For example, `python3 ./personal-budget/main.py /home/pc/Documents/budget/config.json`.

If you'd like to schedule the above script to run on a regular schedule, you can do the following:
1) Assuming you're using a Linux distribution, like Ubuntu, in your terminal, run `crontab -e` to open the `crontab` program.
2) If prompted to select a text editor, choose a text editor.
3) Add a cron expression at the bottom of the file to run the same command above.  For example, if you want to schedule the script to run every day at 8am, you would add this line at the bottom of the `crontab` file (notice the use of absolute paths):
```
0 8 * * * python3 /home/pc/repos/personal-budget/personal_budget/personal-budget/main.py /home/pc/Documents/budget/config.json >/dev/null 2>&1
```

You can use the following site to generate a cron job:  https://crontab-generator.org/

###Using the Docker Image
1) Pull the docker image `docker pull personal-budget:latest`.
2) Run the image with `sudo docker run -v /aboslute/path/to/budget/directory:/personal-budget/data --publish 5000:5000 personal-budget:latest`
This command will mount your budget directory into the container and publish or "connect" the container's port 5000 to your
   local machine's port 5000 so that your browser can communicate with the API.
3) Go to `http://localhost:5000` in a browser to see the personal-budget UI.
4) To kill the container, open another terminal, run `docker ps`, get the ID of the container, and then run `docker stop <ID>`.