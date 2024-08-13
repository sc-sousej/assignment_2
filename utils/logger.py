import logging

def setup_logger(log_file_name):
    # Create a logger object
    logger = logging.getLogger(log_file_name)
    
    # Set the logging level (INFO, DEBUG, ERROR, etc.)
    logger.setLevel(logging.INFO)
    
    # Create a file handler to log to the specified file
    file_handler = logging.FileHandler(log_file_name)
    
    # Create a formatter for the logs
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Add the formatter to the file handler
    file_handler.setFormatter(formatter)
    
    # Add the file handler to the logger
    logger.addHandler(file_handler)
    
    return logger
