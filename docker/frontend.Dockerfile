FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY frontend/ .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Run the application in development mode
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
