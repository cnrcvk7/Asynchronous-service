# pull base image
FROM node:20-alpine

# set our node environment, either development or production
# defaults to production, compose overrides this to development on build and run
ARG NODE_ENV=production
ENV NODE_ENV $NODE_ENV

# add in your own IP that was assigned by EXPO for your local machine
ARG IP_ADDRESS="0.0.0.0"
ENV REACT_NATIVE_PACKAGER_HOSTNAME $IP_ADDRESS
ENV EXPO_PUBLIC_IP_ADDRESS $IP_ADDRESS

# install global packages
ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV PATH /home/node/.npm-global/bin:$PATH
RUN npm i -g npm@latest expo-cli@latest
#We need to install this inorder to start a tunnel on the docker conatiner
RUN yarn add @expo/ngrok

# install dependencies first
WORKDIR /opt/my-app
COPY package.json ./
RUN yarn install
COPY . .

CMD ["npx", "expo", "start"]