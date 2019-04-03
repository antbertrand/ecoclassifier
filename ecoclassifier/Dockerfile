FROM ufoym/deepo:all-py36-cpu

# Copy the current directory contents into the container at /app
# ADD ./src/ /src/
ADD . /ecoclassifier/
WORKDIR /ecoclassifier/src

# Here's our nice application!
RUN pip install --upgrade pip
RUN pip install -r /ecoclassifier/requirements.txt
RUN pip install -e /ecoclassifier/

# Install Snap7
RUN add-apt-repository ppa:gijzelaar/snap7 -y && \
    apt-get update && \
    apt-get install -y libsnap7-1 libsnap7-dev

# Install Pylon.
# File is taken from: https://www.baslerweb.com/en/sales-support/downloads/software-downloads/pylon-5-2-0-linux-x86-64-bit-debian/
COPY ./pylon_5.2.0.13457-deb0_amd64.deb /tmp/pylon.deb
RUN apt install /tmp/pylon.deb

# Entrypointing
COPY ./docker-entrypoint.sh /usr/local/bin/

# Use dockerize to handle configuration templates and container readyness sync.
# See: https://github.com/jwilder/dockerize
ENV DOCKERIZE_VERSION v0.5.0
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Execute migrations and set superuser info (ONCE THE DB IS UP AND RUNNING!!)
# ENTRYPOINT ["dockerize", "-wait", "tcp://db:5432", "-timeout", "30s", "/usr/local/bin/docker-entrypoint.sh"]
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Don't do very interesting things here
CMD ["/bin/bash"]
