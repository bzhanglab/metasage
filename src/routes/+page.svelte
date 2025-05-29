<script lang="ts">
	import SunBurst from '$lib/charts/SunBurst.svelte';
	import CorrRank from '$lib/charts/CorrRank.svelte';
	import Logo from '$lib/components/Logo.svelte';
	import NavBar from '$lib/components/NavBar.svelte';
	import { onMount } from 'svelte';

	let metabolite_search: HTMLInputElement;
	let gene_search: HTMLInputElement;
	let cohort_search: HTMLSelectElement;
	onMount(() => {
		// Initialize the search fields with empty values
		metabolite_search.onchange = () => {
			const metabolite = metabolite_search.value;
			if (metabolite) {
				window.location.href = `/search?metabolite=${metabolite}`;
			}
		};
		gene_search.onchange = () => {
			const gene = gene_search.value;
			if (gene) {
				window.location.href = `/search?gene=${gene}`;
			}
		};
		cohort_search.onchange = () => {
			const cohort = cohort_search.value;
			if (cohort) {
				window.location.href = `/search?cohort=${cohort}`;
			}
		};
	});
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

<div class="my-10 grid grid-cols-1 gap-50 px-50 md:grid-cols-2 lg:grid-cols-2">
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

	<fieldset class="fieldset rounded-box h-max w-full border border-gray-100 p-4 shadow-sm">
		<legend class="fieldset-legend">Search</legend>
		<label for="metabolite_search" class="label font-black">Search for Metabolite</label>
		<input
			bind:this={metabolite_search}
			id="metabolite_search"
			type="text"
			class="input w-full"
			placeholder="HMDB ID (i.e. HMDB00012)"
		/>
		<label for="gene_search" class="label font-black">Search for Gene</label>
		<input
			bind:this={gene_search}
			id="gene_search"
			type="text"
			class="input w-full"
			placeholder="Gene Symbol (i.e. ESR1)"
		/>
		<label for="cohort_search" class="label font-black">Search by Cohort</label>
		<select bind:this={cohort_search} id="cohort_search" class="select w-full text-gray-500">
			<option disabled selected>Select Cohort</option>
			<option>OV</option>
			<option>CCRCC1</option>
			<option>CCRCC2</option>
			<option>CCRCC3</option>
			<option>CCRCC4</option>
			<option>PDAC</option>
			<option>BRCA1</option>
			<option>BRCA2</option>
			<option>COAD</option>
			<option>PRAD</option>
			<option>HurthleCC</option>
			<option>DLBCL</option>
			<option>GBM</option>
			<option>HCC</option>
			<option>ICC</option>
		</select>
	</fieldset>
</div>

<div class="w-full px-50">
	<h2 class="card-title">Predictable Analytes Per Cohort</h2>
	<CorrRank></CorrRank>
</div>
