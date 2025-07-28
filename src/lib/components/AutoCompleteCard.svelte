<script lang="ts">
	type AutoCompleteCardProps = {
		heading?: string;
		description?: string;
		search_value?: string | null;
	};

	const {
		heading = 'Alanine',
		description = 'HMDB: HMDB0000122',
		search_value = null
	}: AutoCompleteCardProps = $props();

	if (!heading || !description) {
		throw new Error('Heading and description are required props.');
	}
	let card_value = $state(search_value || `${heading} ${description}`);
</script>

<div class="card bg-base-100 shadow-sm w-full">
	<div class="card-body">
		<h2 class="card-title">{heading}</h2>
		<p class="text-sm text-gray-500">{description}</p>
	</div>
</div>
