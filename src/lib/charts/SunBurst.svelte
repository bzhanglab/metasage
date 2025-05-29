<script lang="ts">
	import * as echarts from 'echarts/core';
	import { SunburstChart } from 'echarts/charts';
	import academic_theme from '$lib/charts/academic.json';
	// Import the title and tooltip components
	import {
		TitleComponent,
		TooltipComponent,
	} from 'echarts/components';
	// Import the Canvas renderer
	import { CanvasRenderer } from 'echarts/renderers';
	import { onMount } from 'svelte';
	echarts.registerTheme('academic', academic_theme);
	// Register the required components
	echarts.use([
		SunburstChart,
		TitleComponent,
		TooltipComponent,
		CanvasRenderer
	]);
	let chart_div: HTMLDivElement;
	onMount(() => {
		const myChart = echarts.init(chart_div, 'academic');
		const data = [
			{
				name: 'RNA',
				children: [
					{ name: 'OV', value: 109 },
					{ name: 'CCRCC1', value: 54 },
					{ name: 'CCRCC2', value: 93 },
					{ name: 'CCRCC3', value: 205 },
					{ name: 'CCRCC4', value: 227 },
					{ name: 'PDAC', value: 44 },
					{ name: 'BRCA1', value: 67 },
					{ name: 'BRCA2', value: 29 },
					{ name: 'COAD', value: 16 },
					{ name: 'PRAD', value: 59 },
					{ name: 'HurthleCC', value: 74 },
					{ name: 'DLBCL', value: 58 },
					{ name: 'GBM', value: 4 },
					{ name: 'HCC', value: 49 },
					{ name: 'ICC', value: 58 }
				]
			},
			{
				name: 'Metabolite',
				children: [
					{ name: 'OV', value: 36 },
					{ name: 'CCRCC1', value: 16 },
					{ name: 'CCRCC2', value: 26 },
					{ name: 'CCRCC3', value: 51 },
					{ name: 'CCRCC4', value: 85 },
					{ name: 'PDAC', value: 9 },
					{ name: 'BRCA1', value: 19 },
					{ name: 'BRCA2', value: 11 },
					{ name: 'COAD', value: 7 },
					{ name: 'PRAD', value: 35 },
					{ name: 'HurthleCC', value: 19 },
					{ name: 'DLBCL', value: 30 },
					{ name: 'GBM', value: 1 },
					{ name: 'HCC', value: 6 },
					{ name: 'ICC', value: 12 }
				]
			}
		];

		const option = {
			tooltip: {},
			series: {
				type: 'sunburst',
				sort: 'asc',
				emphasis: {
					focus: 'ancestor'
				},
				data: data,
				radius: [0, '90%'],
				label: {
					rotate: 'radial',
					minAngle: 5,
                    
				},
                levels: [{}, {}, {nodeClick: false, label: {formatter: '{b} (n = {c})',
                    fontSize: 9}}]
			}
		};
		myChart.setOption(option);
		window.addEventListener('resize', () => {
			myChart.resize();
		});
	});
</script>

<div class='w-full h-full' bind:this={chart_div}></div>