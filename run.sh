# create new image for application
sudo docker image build . -t django_app:0.0.1

# start docker-compose

sudo docker-compose up -d