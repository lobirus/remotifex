FROM node:22-alpine AS base

WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm install

# Copy source
COPY . .

# Build
RUN npm run build

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]

# Development target
FROM node:22-alpine AS dev

WORKDIR /app

COPY package.json ./
RUN npm install

EXPOSE 3000

CMD ["npm", "run", "dev"]
