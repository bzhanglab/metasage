<script>
	import NavBar from "$lib/components/NavBar.svelte";

  export let data;
  const { content: Content, metadata } = data;
</script>

<NavBar></NavBar>
<article class="prose lg:prose-l p-4">
  <h1>{metadata.title}</h1>
  <Content />
</article>