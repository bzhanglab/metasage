<script lang="ts">
    import Logo from "$lib/components/Logo.svelte";
import NavBar from "$lib/components/NavBar.svelte";
</script>
<NavBar></NavBar>
<div class="hero pt-20">
  <div class="hero-content text-center">
    <div class="max-w-md">
      <h1 class="text-5xl font-bold"><Logo></Logo></h1>
      <p class="py-6">
                Robust discovery of metabolite regulation and therapeutic insights in cancer.
      </p>
      <button class="btn btn-primary">View Results</button>
    </div>
  </div>
</div>

<div class="prose lg:prose-l p-10 prose-slate">
    <div class="card bg-base-100 w-96 shadow-sm">
  <figure>
    <img
      src="https://img.daisyui.com/images/stock/photo-1606107557195-0e29a4b5b4aa.webp"
      alt="Shoes" />
  </figure>
  <div class="card-body">
    <h2 class="card-title">Card Title</h2>
    <p>A card component has a figure, a body part, and inside body there are title and actions parts</p>
    <div class="card-actions justify-end">
      <button class="btn btn-primary">Buy Now</button>
    </div>
  </div>
</div>
</div>