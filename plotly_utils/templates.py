import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px

MARKERS = ['circle', 'cross', 'x', 'triangle-up', 'star', 'hexagram', 'square', 'diamond', 'hourglass', 'bowtie', 'pentagon', 'triangle-down', 'triangle-left', 'triangle-right', 'star-triangle-up', 'star-triangle-down', 'star-square', 'star-diamond', 'diamond-tall', 'diamond-wide', 'triangle-ne', 'triangle-se', 'triangle-sw', 'triangle-nw',  'hexagon', 'hexagon2', 'octagon']

# MY TEMPLATE ----------------------------------------------------------

my_template = pio.templates['plotly']
my_template.data.scatter = [
	go.Scatter(
		marker = dict(
			symbol = s, 
			line = dict(
					width = .5,
			),
		), 
		error_y = dict(
			width = 1, 
			thickness = .8
			)
		) for s in MARKERS
]
my_template.layout['font'] = dict(
	family = 'Comfortaa',
)
my_template.layout['hoverlabel'] = dict(
	font_family = 'Comfortaa'
)
my_template.layout['legend'] = dict(
	valign = 'top',
)

# BORING THESIS TEMPLATE -----------------------------------------------

boring_thesis_template = pio.templates['simple_white']
boring_thesis_template.data.scatter = [
	go.Scatter(
		marker = dict(
			symbol = s, 
			line = dict(
					width = .5,
			),
		), 
		error_y = dict(
			width = 1, 
			thickness = .8
			)
		) for s in MARKERS
]
boring_thesis_template.layout['font'] = dict(
	family = 'serif',
)
boring_thesis_template.layout['hoverlabel'] = dict(
	font_family = 'serif'
)
boring_thesis_template.layout['legend'] = dict(
	valign = 'top',
)
for xy in {'x','y'}:
	boring_thesis_template.layout[f'{xy}axis'].update(
		dict(
			mirror = 'allticks',
			ticks = 'inside',
			showline = True,
		),
	)
for plot_type in {'contour','heatmap','heatmapgl','histogram2d','histogram2dcontour'}:
	boring_thesis_template['data'][plot_type][0]['colorscale'] = px.colors.sequential.Peach
