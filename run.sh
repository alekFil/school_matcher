#!/bin/bash
docker build -t school_matcher .
docker run -d -p 8000:8000 school_matcher
