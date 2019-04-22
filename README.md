## Brief
Fork of GPT-2-117M to run a telegram.me bot or to communicate with the current bot. This repository is meant to be a starting point for researchers and engineers to experiment with GPT-2-117M.  While GPT-2-117M is less proficient than GPT-2-1.5B, it is useful for a wide range of research and applications which could also apply to larger models.

## To contact the bot:
Follow this link:
http://telegram.me/gpt2gpubot

## To set the bot up yourself:
(You will require Ubuntu 18.04 LTS.)

Install docker for nvidia:
```
# Install Docker CE + nvidia-docker version 2.0
sudo apt-get remove -y docker docker-engine docker.io \
    && sudo apt-get update \
    && sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common \
    &&  curl -fsSL 'https://download.docker.com/linux/ubuntu/gpg' | sudo apt-key add - \
    && sudo add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu  $(lsb_release -cs) stable" \
    && sudo apt-get update \
    && sudo apt-get install -y docker-ce \
    && sudo docker run hello-world \
    && sudo docker volume ls -q -f driver=nvidia-docker \
    | xargs -r -I{} -n1 docker ps -q -a -f volume={} \
    | xargs -r docker rm -f \
    && sudo apt-get purge -y nvidia-docker || true \
    && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
    && curl -s -L "https://nvidia.github.io/nvidia-docker/$(. /etc/os-release; echo $ID$VERSION_ID)/nvidia-docker.list" \
    | sudo tee /etc/apt/sources.list.d/nvidia-docker.list \
    && sudo apt-get update \
    && sudo apt-get install -y nvidia-docker2 \
    && sudo pkill -SIGKILL dockerd \
    && sudo docker run --runtime=nvidia --rm nvidia/cuda:9.0-base nvidia-smi \
    && echo Docker CE and nvidia-docker successfully installed.
```
Install git and git-clone:
```
sudo apt install git
git clone https://github.com/SendingAFax/gpt-2-telegram.git
```
Contact @botfather and get a bot key put this key in place of BOTKEY in src/meow.py
Edit the settings as you wish, then build the docker container:
```
cd gpt-2-telegram/
sudo docker build -t gpt-nvidia -f Dockerfile.gpu .
```
Run the docker container:
```
sudo docker run --runtime=nvidia --net=host -t gpt-nvidia
```
Follow the URL to the jupyter web interface from the docker window, then click New -> Terminal.
Type the following:

```
src/meow.py
```
Your bot should now be running.

Have fun!

## License

[MIT](./LICENSE)
