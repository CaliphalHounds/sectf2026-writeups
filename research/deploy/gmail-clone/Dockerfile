FROM node:18-alpine AS builder
WORKDIR /app

COPY package*.json ./
COPY tailwind.config.js ./
COPY src/ ./src/

RUN npm init -y && npm install -D tailwindcss
RUN npx tailwindcss -i ./src/input.css -o ./style.css

FROM nginx:stable-alpine
WORKDIR /usr/share/nginx/html

RUN rm -rf ./*

COPY . .

RUN sed -i 's/listen[[:space:]]*80;/listen 7635;/g' /etc/nginx/conf.d/default.conf

EXPOSE 7635

CMD ["nginx", "-g", "daemon off;"]
