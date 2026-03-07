# Build Stage
FROM node:18-alpine AS build

WORKDIR /app

# Install dependencies first for caching layer
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build

# Production Stage
FROM nginx:alpine

# Copy custom Nginx configuration to handle React Router correctly
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built React app from the previous stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port (Internal to container network)
EXPOSE 80

# Run nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
