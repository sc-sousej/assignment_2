#!/bin/bash

# Run t1.py and t2.py simultaneously
python3 t1.py &  # Run t1.py in the background
python3 t2.py &  # Run t2.py in the background

# Wait for both scripts to complete
wait

echo "Both scripts have completed."
