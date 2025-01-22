# Step 1: Use an official Node.js image as the base image
FROM node:16

# Step 2: Set the working directory in the container
WORKDIR /app

COPY . /app

# Step 4: Install dependencies
RUN npm install

# Step 5: Expose the port that your app will run on
EXPOSE 8080

# Step 6: Command to run the app
CMD ["npm", "run", "dev"]
