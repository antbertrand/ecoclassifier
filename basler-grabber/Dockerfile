# See https://www.learnopencv.com/install-opencv-docker-image-ubuntu-macos-windows/
FROM spmallick/opencv-docker:opencv

# Set the working directory to /app and deploy requirements
# Little hack found here: https://stackoverflow.com/questions/34398632/docker-how-to-run-pip-requirements-txt-only-if-there-was-a-change
COPY ./src/requirements.txt /src/requirements.txt
WORKDIR /src
RUN pip install -r ./requirements.txt

# Copy the current directory contents into the container at /app
ADD ./src/ /src/

# Here's our nice application!
# RUN pip install --upgrade pip
# RUN pip install -e .

# Make port 8000 available to the world outside this container
# EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED 1

# Prepare our entrypoint command
COPY ./docker-entrypoint.sh /usr/local/bin/

# Use dockerize to handle configuration templates and container readyness sync.
# See: https://github.com/jwilder/dockerize
ENV DOCKERIZE_VERSION v0.5.0
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Execute migrations and set superuser info (ONCE THE DB IS UP AND RUNNING!!)
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Run our app when the container launches
#CMD ["django-admin", "runserver", "0.0.0.0:8000"]
