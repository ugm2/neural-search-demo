"""
Core utils
"""

# Function decorator for selecting which methods are pipelines
# so we can list them properly afterwards
def is_pipeline(f):
    f.is_pipeline = True
    return f
