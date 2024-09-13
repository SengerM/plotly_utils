import numpy
import pandas
from plotly_utils import imshow_logscale
from plotly.express import imshow
from pathlib import Path

SAVE_PLOTS_HERE = Path('/tmp')/'plotly_utils_examples'
SAVE_PLOTS_HERE.mkdir(exist_ok=True)

# Create some data to plot:
y = numpy.linspace(-2,2,99)
x = numpy.linspace(-1,1,111)
xx,yy = numpy.meshgrid(x,y)
data = pandas.DataFrame(
	data = 10**(xx+yy) + numpy.sinh(xx)**2,
	columns = pandas.Index(
		data = x,
		name = 'x values',
	),
	index = pandas.Index(
		data = y,
		name = 'y values',
	),
)

# Plot:
for scale,func in {'lin':imshow, 'log':imshow_logscale}.items():
	fig = func(
		title = f'{scale} scale',
		img = data,
		origin = 'lower',
		aspect = 'auto',
		labels = {'color': 'f(x,y)=10<sup>x+y</sup>+sinh(x)<sup>2</sup>'},
	)
	fig.write_html(
		SAVE_PLOTS_HERE/f'{scale}_scale.html',
		include_plotlyjs = 'cdn',
	)

print(f'Plots saved in {SAVE_PLOTS_HERE}')
