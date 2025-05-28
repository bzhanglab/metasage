<script lang="ts">
	import SunBurst from '$lib/charts/SunBurst.svelte';
	import Logo from '$lib/components/Logo.svelte';
	import NavBar from '$lib/components/NavBar.svelte';
</script>

<NavBar></NavBar>
<div class="hero pt-20">
	<div class="hero-content text-center">
		<div class="max-w-md">
			<h1 class="text-5xl font-bold"><Logo></Logo></h1>
			<p class="py-6">
				Robust discovery of metabolite regulation and therapeutic insights in cancer.
			</p>
			<a class="btn btn-primary btn-outline" href="/overview">View Results</a>
		</div>
	</div>
</div>

<div class="px-100 grid grid-cols-1 gap-50 my-10 md:grid-cols-2 lg:grid-cols-2">
	<div class="card bg-base-100 h-130 w-full shadow-sm">
		<div class="card-body h-full w-full">
			<h2 class="card-title">Identified Important Analytes</h2>
			<SunBurst></SunBurst>
			<p class="text-sm text-gray-500">
				This chart shows the number of analytes identified in each cancer cohort, categorized by
				analyte type. The size of each segment represents the number of significant analytes.
			</p>
		</div>
	</div>
  <div class="card bg-base-100 h-130 w-full shadow-sm">
		<div class="card-body h-full w-full">
			<h2 class="card-title">Identified Important Analytes</h2>
			<SunBurst></SunBurst>
			<p class="text-sm text-gray-500">
				This chart shows the number of analytes identified in each cancer cohort, categorized by analyte type. The size of each segment represents the number of significant analytes.
			</p>
		</div>
	</div>
</div>
