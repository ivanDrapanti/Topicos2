# Use the official Python image as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt
#py -m
# Copy the content of the local src directory to the working directory
COPY . .

# Expose the port on which your app will run
EXPOSE 5000

# Define the command to run your application
CMD ["python", "mongo_app.py"]