# Lab Algorithmisches Beweisen SoSe 2024

This repository contains all my code, testing and documentation from the Lab sessions of "Algorithmisches Beweisen" - a university course at the Friedrich Schiller University in Jena.

## Repository Structure

### formula_generation
This module allows for generating random formulas, pebbling formulas and pigeonhole formulas for given parameters.

### solvers
This module contains all solvers and some necessary util functions.

### tasks
This folder contains all the tasks of the different lab sessions.

### benchmarks.ipynb and test_solver.py
benchmarks does a statistical analysis of different solvers and therefore fulfills the tasks at the end of every lab session and the lab 11.
test_solver.py contains a class that facilitates the analyses in the benchmarks notebook.

## Getting started
To run all code, it would be advisable to install a fresh python environment and include all packages specified in the requirements.txt or environment.yml file. This can be automatically done using pip:

    python3 -m venv .venv
    pip install -r requirements.txt
or using conda:

    conda env create -f environment.yml
