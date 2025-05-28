<script lang="ts">
import NavBar from "$lib/components/NavBar.svelte";
import DataOverview from "$lib/charts/DataOverview.svelte";
	import SunBurst from "$lib/charts/SunBurst.svelte";
</script>

<NavBar>
</NavBar>
<div class="p-10">
<DataOverview></DataOverview>
<div class="w-1/2 h-100"><SunBurst></SunBurst></div>
</div>