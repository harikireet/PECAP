from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

setup(
    name="PCAP StoryTeller",
    version="0.1",
    author="dmt",
    
    # 1. Logic to find all code folders
    packages=find_packages(),
    
    # 2. Logic to read from requirements.txt
    install_requires=requirements,
    
    # 3. CRITICAL: This ensures HTML and CSS files are included in the install!
    include_package_data=True,
    
    # 4. Added for educational value: explains what this file does
    description="A modern network forensics tool designed for education.",
)