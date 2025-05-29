<script lang="ts">
	import NavBar from '$lib/components/NavBar.svelte';
	import { onMount } from 'svelte';
	import { derived } from 'svelte/store';
	let params = $state({
		gene: '',
		metabolite: '',
		cohort: ''
	});
	// Get URL search parameters as a derived store
	onMount(() => {
		// This will run once when the component is mounted
		// You can perform any initialization here if needed
		const urlParams = new URLSearchParams(window.location.search);
		params = {
			gene: urlParams.get('gene') || '',
			metabolite: urlParams.get('metabolite') || '',
			cohort: urlParams.get('cohort') || ''
		};
	});
</script>

<NavBar></NavBar>

<div class="p-10">
	<h1 class="text-2xl">Search Results</h1>

	{#if params}
		<p>Here are the search results based on your query:</p>

		<ul>
			<li><strong>Gene:</strong> {params.gene}</li>
			<li><strong>Metabolite:</strong> {params.metabolite}</li>
			<li><strong>Cohort:</strong> {params.cohort}</li>
		</ul>
	{:else}
		<p>No search parameters provided. Please enter a search term.</p>
	{/if}
</div>
