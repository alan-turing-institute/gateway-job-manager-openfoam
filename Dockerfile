FROM base/archlinux:2018.09.01

# Install a bunch of extra packages
RUN pacman -Sy --noconfirm sudo python python-pip openssh vim supervisor git gcc python-psycopg2

# Set up a UTF 8 locale
RUN sed -i "s/#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/" /etc/locale.gen
RUN locale-gen
ENV LANG=en_US.UTF-8

# Copy over the code to run
ADD . /app
WORKDIR /app

# Now install the python requirements
RUN pip install -r requirements.txt

# Set up the application state
ENV FLASK_APP app.py

RUN mkdir -p /var/log/supervisor && \
    mkdir -p /etc/supervisor/conf.d

ADD supervisor/supervisor.conf /etc/supervisor.conf
ADD supervisor/app.conf /etc/supervisor/conf.d/app.conf

RUN useradd -mU -s /bin/bash testuser && echo 'testuser:testuser' | chpasswd
RUN echo "docker ALL=(ALL:ALL) ALL" | (EDITOR="tee -a" visudo)
RUN echo "AllowUsers testuser" >> /etc/ssh/sshd_config

RUN [ ! -f /etc/ssh/ssh_host_rsa_key ] && ssh-keygen -A;

ADD keys/config /root/.ssh/config
ADD keys/config /home/testuser/.ssh/config

CMD ["supervisord", "-c", "/etc/supervisor.conf"]
