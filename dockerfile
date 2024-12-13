FROM apache/airflow:2.10.2

# Set the working directory to your project root
WORKDIR /DE_capstone_project

# Set PYTHONPATH to the project root which helps Python locate your modules.
ENV PYTHONPATH=/DE_capstone_project

# Copy the project files into the container
COPY . /DE_capstone_project

# Copy requirements.txt and install additional Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint to use the Airflow command line interface
ENTRYPOINT ["airflow"]

# Default command to run the webserver
CMD ["webserver"]