# A simple Dash web app for Data Visualization

I once got this data as part of an evaluation, and since the work is already done, I figured I might as well show the results here. It's a simple web-app built in Dash (which is essentially React for Python) and can be run in localhost by clonning the repo and running the setup shell script, as stated below.

<br>

## What's inside

Analysis of a time series that contains the following steps:
- Data Check: Check for uncorrectly formatted datapoints.
- Outliers: Check for possible outliers within the data
- Points of interest: Find local minima and maxima
- Periodicity: Check auto-corretalion to attest for periodicity.
- Prediction: Extrapolate the trend into the next two hours.

<br>

## Installation

```
source setup.sh
```
<br>

## Usage

```
make run
```
