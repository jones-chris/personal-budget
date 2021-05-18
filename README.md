# Personal Budget

## Use

### Initial Set Up
1. Create a directory/folder on your computer that will hold all your personal financial transactions.

### Starting the app
1. Copy the absolute file path of the directory/folder you created in the step above.
   - NOTE:  On Windows this will be something like `C://the/absolute/path`.  On Mac or Linux this will be something like 
     `/the/absolute/path`.
2. If you have docker installed on your computer already, then run `docker pull personal-budget:latest` to pull the docker 
   image containing both the backend and UI codebase.  
   - NOTE:  If docker is not installed, then install docker.  Once it's installed, continue this step.
3. Start a docker container using the image by running `docker run -v <path from step #2 goes here>:/personal-budget/data --publish 5000:5000 personal-budget:latest` 
   and substitute the absolute file path from step #2 where the `<path from step #2 goes here>` placeholder is.
4. Open a browser and go to `http://localhost:5000`.  You should see the following:
   ![home page](./readme_images/home.png)

### Using the app
#### Transactions
- You can view your transactions in the 

### Stopping the app
5. To stop the docker container open another terminal, run `docker ps`, get the ID of the container, and then run `docker stop <ID>`
   and replace the docker container ID where the `<ID>` placeholder is.
   
