FROM python:3.8-slim

# Copy personal-budget project's backend and UI directories.
RUN mkdir personal-budget
WORKDIR personal-budget
COPY ./backend ./backend
COPY ./ui ./ui
COPY ./manifest.json .
COPY ./run.sh .
COPY ./run-backend.sh .
COPY ./run-ui.sh .

# Create the directory that the user's budget data will be mounted into.
RUN mkdir data

# Install backend dependencies.
RUN pip3 install -r ./backend/requirements.txt

# Install npm and UI dependencies.
RUN apt-get update -y
RUN apt-get install nodejs -y
RUN apt-get install npm -y
RUN npm --prefix ./ui install

# Expose port 5000 for the backend API and port 3000 for the UI.
EXPOSE 5000
EXPOSE 3000

CMD ./run.sh