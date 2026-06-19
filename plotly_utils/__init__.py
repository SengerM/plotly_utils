import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy
import pandas

def update_recursively(
	self,
		# The dictionary to be updated.
	other,
		# The dictionary to be used to update `self`.
)->dict:
	"""Similar to [`dict.update`](https://docs.python.org/3/library/stdtypes.html#dict.update) but recursive."""
	for key,item in self.items():
		if key in other:
			if isinstance(item,dict):
				update_recursively(self[key], other[key])
			else:
				self[key] = other[key]
	return self

def px_with_grouped_legend(px_function, **kwargs):
	"""
	Universal wrapper for any plotly.express function that automatically
	applies grouped legend when multiple dimensions are used.

	Usage:
		fig = px_with_grouped_legend(px.line, data_frame=df, x='time',
									 y='value', color='category', symbol='type')
		fig = px_with_grouped_legend(px.scatter, data_frame=df, x='x',
									 y='y', color='group')
	"""
	fig = px_function(**kwargs)
	graph_dimensions = {k: kwargs[k] for k in ['color', 'symbol', 'line_dash']
					   if k in kwargs}
	if graph_dimensions:
		add_grouped_legend(fig, kwargs['data_frame'], kwargs.get('x'),
						  graph_dimensions, kwargs.get('labels'))
	return fig


def add_grouped_legend(fig, data_frame, x, graph_dimensions, labels:dict=None):
	"""Create a grouped legend with one entry per unique value of each dimension.
	
	NOTE: The legend is non-interactive (clicking items won't hide/show traces)
	because Plotly's legendgroup system doesn't support multi-dimensional interactivity.
	
	- fig: The figure in which to add such grouped legend.
	- data_frame: The data frame from which to create the legend.
	- x: The x-axis column name.
	- graph_dimensions: A dictionary with arguments like 'color', 'symbol', 'line_dash'.
	- labels: Optional dictionary to rename dimension column names in the legend.
	"""
	if labels is None:
		labels = dict()
	
	# Store original number of traces
	original_traces = list(fig.data)
	
	# Hide all existing legend entries
	for trace in original_traces:
		trace.showlegend = False
	
	# Remove the legend title and disable legend interactivity
	fig.update_layout(
		legend_title_text='',
		legend=dict(
			itemclick=False,  # Disable single click
			itemdoubleclick=False,  # Disable double click
		)
	)

	# Build a mapping of dimension -> unique values from the data
	dimension_values = {}
	for dimension, column_name in graph_dimensions.items():
		dimension_values[dimension] = sorted(data_frame[column_name].unique())

	# Create a mapping from trace name to trace properties
	trace_to_dimensions = {}
	for idx, trace in enumerate(original_traces):
		trace_dims = {}
		# Match trace to dimension values based on trace.name
		for dimension, column_name in graph_dimensions.items():
			for value in dimension_values[dimension]:
				if str(value) in str(trace.name):
					trace_dims[dimension] = value
					break
		trace_to_dimensions[idx] = trace_dims

	# Collect new legend traces to add at the end
	new_legend_traces = []

	# Track which dimensions have already had their title set
	dimensions_with_title = set()

	# For each dimension, create legend entries
	# NOTE: Only the last dimension will be fully interactive due to legendgroup limitations
	for dimension, column_name in sorted(graph_dimensions.items()):
		dimension_label = labels.get(column_name, column_name)

		for value in dimension_values[dimension]:
			# Find all original traces that match this dimension value
			matching_trace_indices = []
			representative_trace = None
			for idx, trace in enumerate(original_traces):
				dims = trace_to_dimensions[idx]
				if dims.get(dimension) == value:
					matching_trace_indices.append(idx)
					if representative_trace is None:
						representative_trace = trace

			if representative_trace is None:
				continue

			# Create a new trace for the legend entry
			legend_trace = px.line(
				data_frame.head(1), # Just need one point
				x=x,
				y=numpy.full(1, float('NaN')), # Invisible
				**{dimension: column_name} # Pass the dimension
			)

			# Configure the legend trace
			for new_trace in legend_trace.data:
				# Copy visual properties from the representative trace
				if dimension == 'color':
					if hasattr(representative_trace, 'line') and representative_trace.line:
						new_trace.line.color = representative_trace.line.color
					if hasattr(representative_trace, 'marker') and representative_trace.marker:
						new_trace.marker.color = representative_trace.marker.color
				elif dimension == 'symbol':
					if hasattr(representative_trace, 'marker') and representative_trace.marker:
						new_trace.marker.symbol = representative_trace.marker.symbol
						# Use black color for symbol-only entries
						new_trace.marker.color = '#000000'
						new_trace.line.color = '#000000'
				elif dimension == 'line_dash':
					if hasattr(representative_trace, 'line') and representative_trace.line:
						new_trace.line.dash = representative_trace.line.dash
						new_trace.marker.color = '#000000'
						new_trace.line.color = '#000000'

				# Set legend properties
				new_trace.name = str(value)
				# Create a legendgroup that includes all matching original traces
				new_trace.legendgroup = f"{dimension}_{value}"

				# Only set legendgrouptitle on the first trace of each dimension
				if dimension not in dimensions_with_title:
					new_trace.legendgrouptitle = dict(text=dimension_label)
					dimensions_with_title.add(dimension)

				new_trace.showlegend = True
				new_trace.hoverinfo = 'skip'

				# Link this legend trace to all matching original traces
				# by adding them to the same legendgroup
				# NOTE: This will overwrite previous legendgroup assignments,
				# so only the last dimension will be interactive
				for idx in matching_trace_indices:
					original_traces[idx].legendgroup = f"{dimension}_{value}"

				# Collect the legend trace
				new_legend_traces.append(new_trace)

	# Add all new legend traces at once
	for trace in new_legend_traces:
		fig.add_trace(trace)


def add_grouped_legend_old(fig, data_frame, x, graph_dimensions, labels:dict=None):
	"""Create a grouped legend based on the example here https://stackoverflow.com/a/69829305/8849755
	- fig: The figure in which to add such grouped legend.
	- data_frame: The data frame from which to create the legend, in principle it should be the same that was plotted in `fig`.
	- graph_dimensions: A dictionary with the arguments such as `color`, `symbol`, `line_dash` passed to plotly.express functions you want to group, with the names of the columns in the data_frame."""
	if labels is None:
		labels = dict()
	param_list = [{'px': {dimension: dimension_value}, 'lg': {'legendgrouptitle_text': (dimension_value if labels.get(dimension_value) is None else labels.get(dimension_value))}} for dimension, dimension_value in sorted(graph_dimensions.items())]
	legend_traces = []
	for param in param_list:
		this_dimension_trace = px.line(
			data_frame,
			x = x,
			y = numpy.full(len(data_frame), float('NaN')),
			**param["px"],
		).update_traces(
			**param["lg"],
			legendgroup = str(param["px"]),
			line_width = 0 if 'symbol' in param['px'] else None,
		)
		if 'color' not in param['px']:
			this_dimension_trace.update_traces(
				marker = {'color': '#000000'},
				line = {'color': '#000000'},
			)
		legend_traces.append(this_dimension_trace)
	for t in legend_traces:
		fig.add_traces(t.data)

def line(error_y_mode:str=None, grouped_legend:bool=False, **kwargs):
	"""Extension of `plotly.express.line`.

	Arguments
	---------
	grouped_legend: bool, default `False`
		if `True` a grouped legend will be produced, which is more easy
		to read when multiple categories are used.
	error_y_mode: string, default `None`
		One of `{'bar','band','bars','bands',None}`. `'bar'` and `'bars'`
		are synonyms, the same as `'band'` and `'bands'`. `'bar'` is the
		normal Plotly error bars. `'band'` produces a continuous band.
		`None` (default) is no errors.
	"""
	def process_color(color: str, alpha: float):
		if '#' in color: # This means it is an hex string:
			return f"rgba({tuple(int(data['line']['color'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))},{alpha})".replace('((','(').replace('),',',').replace(' ','')
		elif 'rgb' in color:
			return f'rgba({color.replace("rgb(","").replace(")","")}, {alpha})'.replace(' ','')

	ERROR_MODES = {'bar','band','bars','bands',None}
	if error_y_mode not in ERROR_MODES:
		raise ValueError(f"'error_y_mode' must be one of {ERROR_MODES}, received {repr(error_y_mode)}.")
	if error_y_mode in {'bar','bars',None}:
		fig = px.line(**kwargs)
	elif error_y_mode in {'band','bands'}:
		if 'error_y' not in kwargs:
			raise ValueError(f"If you provide argument 'error_y_mode' you must also provide 'error_y'.")
		figure_with_error_bars = px.line(**kwargs)
		fig = px.line(**{arg: val for arg,val in kwargs.items() if arg != 'error_y'})
		for data in figure_with_error_bars.data:
			x = list(data['x'])
			y_upper = list(data['y'] + data['error_y']['array'])
			y_lower = list(data['y'] - data['error_y']['array'] if data['error_y']['arrayminus'] is None else data['y'] - data['error_y']['arrayminus'])
			y_upper = [_ if _==_ else 0 for _ in y_upper]
			y_lower = [_ if _==_ else 0 for _ in y_lower]
			fig.add_trace(
				go.Scatter(
					x = x+x[::-1],
					y = y_upper+y_lower[::-1],
					fill = 'toself',
					fillcolor = process_color(data['line']['color'], alpha=.3),
					line = dict(
						color = 'rgba(255,255,255,0)'
					),
					hoverinfo = "skip",
					showlegend = False,
					legendgroup = data['legendgroup'],
					xaxis = data['xaxis'],
					yaxis = data['yaxis'],
				)
			)
		# Reorder data as said here: https://stackoverflow.com/a/66854398/8849755
		reordered_data = []
		for i in range(int(len(fig.data)/2)):
			reordered_data.append(fig.data[i+int(len(fig.data)/2)])
			reordered_data.append(fig.data[i])
		fig.data = tuple(reordered_data)

	if grouped_legend == True:
		add_grouped_legend(
			fig = fig,
			data_frame = kwargs['data_frame'],
			x = kwargs.get('x'),
			graph_dimensions = {param: kwargs[param] for param in {'color','symbol','line_dash'} if param in kwargs},
			labels = kwargs.get('labels'),
		)

	return fig

def scatter_histogram(samples, bins='auto', error_y=None, density=None, nan_policy='omit', line_shape='hvh', **kwargs) -> go.Scatter:
	"""Produces a histogram using a *Scatter trace* with `line_shape = 'hvh'`.
	The idea is that it has the same interface as `plotly.graph_objects.Scatter`
	but instead of receiving `x` and `y` it receives the samples and
	creates the `x` and `y` using `numpy.histogram`. Then it is plotted
	as a scatter plot, by default using the `line_shape='hvh'` option.

	Parameters
	----------
	samples: array
		A 1D array with the samples.
	bins: int or sequence of scalars or str, optional
		This is passed to `numpy.histogram`, see its documentation.
	error_y: str, default is None
		This is the dictionary that will be handled to `plotly.graph_objects.Scatter`
		(see [here](https://plotly.com/python/reference/scatter/#scatter-error_y-type)).
		In this function I am adding the functionality that the `type`
		argument of the dictionary can be `'auto'`. In this case the
		error bands are calculated using the binomial expression.
	density: bool, optional
		This is handled to `numpy.histogram` directly, see its documentation
		for details.
	nan_policy: str, default 'omit'
		Options are `'omit'` and `'raise'`. If `'omit'`, then `NaN` values
		in the data are removed. If `'raise'` then `NaN` values in the
		data will raise a `ValueError`. This is the same [behavior adopted
		by scipy](https://docs.scipy.org/doc/scipy-1.8.0/html-scipyorg/dev/api-dev/nan_policy.html).
	line_shape: str, default 'hvh'
		This is handled to `plotly.graph_objects.Scatter`.

	Returns
	-------
	trace: plotly.graph_objects.Scatter
		A `plotly.graph_objects.Scatter` object.

	Example
	-------
	```
	from grafica.plotly_utils.utils import scatter_histogram
	import plotly.graph_objects as go
	import numpy as np

	samples = np.random.randn(999)

	fig = go.Figure()
	fig.add_trace(
		scatter_histogram(
			samples,
			error_y = dict(
				type = 'auto',
				width = 0,
			),
			marker = dict(symbol='circle'),
			mode = 'markers+lines',
		)
	)
	fig.show()
	```
	"""
	if density is not None:
		if not isinstance(density, bool):
			raise TypeError(f'`density` must be `True` or `False`, received object of type {type(density)}.')
	if nan_policy == 'raise' and any(numpy.isnan(samples)):
		raise ValueError(f'`samples` contains NaN values.')
	elif nan_policy == 'omit':
		samples = samples[~numpy.isnan(samples)]
	hist, bin_edges = numpy.histogram(samples, bins=bins, density=density)
	bin_centers = bin_edges[:-1] + numpy.diff(bin_edges)/2
	# Add an extra bin to the left:
	hist = numpy.insert(hist, 0, sum(samples<bin_edges[0]))
	bin_centers = numpy.insert(bin_centers, 0, bin_centers[0]-numpy.diff(bin_edges)[0])
	# Add an extra bin to the right:
	hist = numpy.append(hist,sum(samples>bin_edges[-1]))
	bin_centers = numpy.append(bin_centers, bin_centers[-1]+numpy.diff(bin_edges)[0])

	if isinstance(error_y, dict) and error_y.get('type') == 'auto':
		n = len(samples)
		p = hist/n
		if density == True:
			p *= numpy.diff(bin_centers)[0]*n
		hist_error = (n*p*(1-p))**.5
		if density == True:
			hist_error /= numpy.diff(bin_centers)[0]*n
		error_y['type'] = 'data'
		error_y['array'] = hist_error
		if error_y.get('width') is None:
			error_y['width'] = 1 # Default value that I like.
		if error_y.get('thickness') is None:
			error_y['thickness'] = .8 # Default value that I like.
		if error_y.get('visible') is None:
			error_y['visible'] = True # For me it is obvious that you want to display the errors is you are giving them to me... So I default this to `True`.
	return go.Scatter(x = bin_centers, y = hist, error_y = error_y, line_shape=line_shape, **kwargs)

def scatter_matrix_histogram(data_frame, dimensions=None, contour:bool=True):
	"""Produce a scatter matrix plot (https://plotly.com/python/splom/)
	but with 2D histograms.

	Parameters
	----------
	data_frame: pandas.DataFrame
		Data frame containing the data to plot.
	dimensions: list of str
		Either names of columns in `data_frame`, or pandas Series, or
		array_like objects Values from these columns are used for
		multidimensional visualization.
	"""
	if not isinstance(dimensions, list) or any([not isinstance(s,str) for s in dimensions]) or any([s not in data_frame.columns for s in dimensions]):
		raise TypeError(f'`dimensions` must be a list of strings naming columns in the `data_frame`.')
	data_frame = data_frame[dimensions]

	if contour == False:
		raise NotImplementedError(f'`contour=False` is not implemented yet.')

	fig = make_subplots(
		len(data_frame.columns),
		len(data_frame.columns),
		shared_xaxes = True,
		shared_yaxes = True,
		horizontal_spacing = .01,
		vertical_spacing = .01,
	)
	for n_col, col_name in enumerate(data_frame.columns):
		for n_row, row_name in enumerate(data_frame.columns):
			fig.add_trace(
				go.Histogram2dContour(
					x = data_frame[col_name],
					y = data_frame[row_name],
				),
				row = n_row+1,
				col = n_col+1,
			)
			if n_col == 0:
				fig.update_yaxes(title_text = row_name, row = n_row+1, col = n_col+1)
			if n_row == len(data_frame.columns)-1:
				fig.update_xaxes(title_text = col_name, row = n_row+1, col = n_col+1)
	fig.update_traces(showscale=False)
	return fig

def imshow_logscale(
	# The same as `plotly.express.imshow` but with logarithmic color scale, and contours.
	img,
		# The same as `img` for `plotly.express.imshow`.
	hoverinfo_z_format:str = ':.2e',
		# A formatting string string for displaying the values in the hover boxes for the color scale.
	minor_ticks = 'auto',
		# If `True`, minor ticks (2,3,4,5,...) are shown, if `False` then only major ticks are shown (1,10,100,1000, etc). If `'auto'` then the decision is made according to the orders of magnitude spanned by the data.
	draw_contours:bool = True,
		# If `True`, contour lines for each tick will be added to the plot.
	contours_parameters:dict = None,
		# A dictionary with any arguments to be passed to the function drawing the contours. Available options should be [here](https://plotly.com/python/reference/contour/).
	**kwargs,
		# Any arguments to be passed to [`plotly.express.imshow`](https://plotly.com/python-api-reference/generated/plotly.express.imshow).
):
	"""
	Returns
	-------
	fig: plotly.graph_objects._figure.Figure
		A figure, same as `plotly.express.imshow`.
	"""
	from engineering_notation import EngNumber

	if minor_ticks not in {True,False,'auto'}:
		raise ValueError(f'`minor_ticks` must be True, False or "auto", received {repr(minor_ticks)}. ')

	if not isinstance(draw_contours, bool):
		raise TypeError(f'`draw_contours` must be boolean, received object of type {type(draw_contours)}. ')

	log_data = numpy.log10(img)

	text_auto = kwargs.get('text_auto')
	if text_auto is not None:
		kwargs.pop('text_auto')

	fig = px.imshow(
		img = log_data,
		**kwargs,
	)
	TICKS_VALS = [list(numpy.linspace(10**e,10**(e+1),10)[:-1]) for e in range(-18,12)]
	if minor_ticks == 'auto':
		if numpy.nanmax(log_data) - numpy.nanmin(log_data) > 3:
			minor_ticks = False
	if minor_ticks == False:
		TICKS_VALS = [[_[0]] for _ in TICKS_VALS]
	TICKS_VALS = [_ for l in TICKS_VALS for _ in l]
	ticks_text = [str(EngNumber(_)) for _ in TICKS_VALS]
	fig.update_layout(
		coloraxis_colorbar = dict(
			tickvals = [numpy.log10(_) for _ in TICKS_VALS],
			ticktext = ticks_text,
		),
	)
	fig.data[0].customdata = img
	hover_template = fig.data[0].hovertemplate.split('<br>')
	labels_for_hover_template = [_.split(': %{')[0] for _ in hover_template]
	fig.data[0].hovertemplate = f"{labels_for_hover_template[0]}: %{{x}}<br>{labels_for_hover_template[1]}: %{{y}}<br>{labels_for_hover_template[2]}: %{{customdata{hoverinfo_z_format}}}<extra></extra>"
	if text_auto is not None:
		if text_auto == False:
			pass
		else:
			fig.data[0].text = img
			if text_auto == True:
				fig.data[0].texttemplate = '%{text}'
			elif isinstance(text_auto, str):
				fig.data[0].texttemplate = f'%{{text:{text_auto}}}'
			else:
				raise TypeError(f'`text_auto` of type {type(text_auto)} not valid, I was expecting either `bool` or a `str`. See documentation for Plotly `imshow` function https://plotly.com/python-api-reference/generated/plotly.express.imshow.')

	if draw_contours:
		for tick_val, tick_text in zip(TICKS_VALS, ticks_text):
			CONTOURS_DEFAULT_PARAMETERS = dict(
				contours = dict(
					type = 'constraint',
					operation = '=',
					value = tick_val,
					showlabels = True,
					coloring = 'none',
				),
				line = dict(
					width = .5,
					color = 'black',
				),
				showlegend = False,
				hoverinfo = 'skip',
			)
			if not numpy.ravel(img).min() < tick_val < numpy.ravel(img).max():
				continue
			fig.add_contour(
				z = img,
				y = img.index,
				x = img.columns,
				**(update_recursively(CONTOURS_DEFAULT_PARAMETERS, contours_parameters) if contours_parameters is not None else CONTOURS_DEFAULT_PARAMETERS),
			)
	return fig
