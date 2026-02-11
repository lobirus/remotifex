FROM node:22-alpine AS base

WORKDIR /app

# Install dependencies (skip postinstall — nuxt prepare needs source files)
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts

# Copy source and run nuxt prepare + build
COPY . .
RUN npm run postinstall
RUN npm run build

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]

# Development target
FROM base AS dev

EXPOSE 3000

CMD ["npm", "run", "dev"]
