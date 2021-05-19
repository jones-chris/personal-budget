FROM python:3.8-slim

ENV APP=webapp

# gcc is needed to run uswgi.
RUN apt-get update
RUN apt-get install gcc -y

# Copy personal-budget project's backend directory and frontend assets.
# NOTE:  Make sure the front end assets have been generated by running `npm run build` so that the `./ui/build` directory will not be empty.
RUN mkdir personal-budget
WORKDIR personal-budget
COPY ./backend ./backend
COPY ./ui/build ./ui/build
COPY ./manifest.json .
COPY ./run.sh .
COPY ./run-webapp.sh .
COPY ./run-ofx-import.sh .

# Create the directory that the user's budget data will be mounted into.
RUN mkdir data

# Install backend dependencies.
RUN pip3 install -r ./backend/requirements.txt

# Expose port 5000 for the backend API (which also serves the UI at the root URI).
EXPOSE 5000

CMD ./run.sh