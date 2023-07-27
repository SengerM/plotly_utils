# Plotly utils

My personal package of utilities for doing nice plots with [Plotly](https://plotly.com/python/).

## Installation

```
pip3 install git+https://github.com/SengerM/grafica
```

## Usage example

The example below illustrates the philosophy of this package:
```Python
import grafica
import numpy

x = numpy.linspace(0,1)

for package in {'plotly','matplotlib'}: # The same code produces the plot with each package.
	figure = grafica.new(
		plotter_name=package, # Just tell me which package you want to use, I'll take care of the rest.
	)
	figure.scatter(x, x**2) # Draw a scatter plot.

grafica.show() # Show all plots.

```
More examples in the [tests directory](tests/plotter_tests).
