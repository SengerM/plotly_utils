import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px

MARKERS = ['circle', 'cross', 'x', 'triangle-up', 'star', 'hexagram', 'square', 'diamond', 'hourglass', 'bowtie', 'pentagon', 'triangle-down', 'triangle-left', 'triangle-right', 'star-triangle-up', 'star-triangle-down', 'star-square', 'star-diamond', 'diamond-tall', 'diamond-wide', 'triangle-ne', 'triangle-se', 'triangle-sw', 'triangle-nw',  'hexagon', 'hexagon2', 'octagon']

def set_my_template_as_default():
	my_template = pio.templates['plotly'] # This is not the best approach, because it creates are reference to the original template and will modify it, but I did not find a better way at the moment.
	for plotting_method_name,plotting_method in {'scatter':go.Scatter,'scattergl':go.Scattergl}.items():
		setattr(
			my_template.data,
			plotting_method_name,
			[
				plotting_method(
					**(
						dict(
							marker = dict(
								symbol = s,
								line = dict(
										width = .5,
								),
							),
						) | {
							f'error_{xy}': dict(
								width = 1,
								thickness = .8
							) for xy in {'x','y'}
						}
					)
				) for s in MARKERS
			]
		)
	my_template.layout['legend'] = dict(
		valign = 'top',
	)
	my_template.layout['plot_bgcolor'] = 'rgba(0, 78, 204, .1)'
	for xy in {'x','y'}:
		my_template.layout[f'{xy}axis']['gridcolor'] = 'rgba(255,255,255, .5)'
	my_template.layout['legend']['bgcolor'] = 'rgba(255,255,255, 0)'
	pio.templates['my_template'] = my_template
	pio.templates.default = 'my_template'

def set_boring_thesis_template_as_default():
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
	# ~ for plot_type in {'contour','heatmap','heatmapgl','histogram2d','histogram2dcontour'}:
		# ~ boring_thesis_template['data'][plot_type][0]['colorscale'] = px.colors.sequential.Peach
	boring_thesis_template['data']['histogram'][0]['marker']['line']['width'] = 0
	pio.templates['boring_thesis_template'] = boring_thesis_template
	pio.templates.default = 'boring_thesis_template'
