<script>
	import Logo from './Logo.svelte';
</script>

<div class="navbar bg-base-100">
	<div class="navbar-start">
		<div class="dropdown">
			<div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-5 w-5"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 6h16M4 12h8m-8 6h16"
					/>
				</svg>
			</div>
			<ul class="menu menu-sm dropdown-content">
				<li><a href="/">Home</a></li>
				<li>
					<a href="/overview">View Data</a>
				</li>
				<li><a href="/downloads">Downloads</a></li>
			</ul>
		</div>
		<a class="btn btn-ghost text-xl" href="/"><Logo></Logo></a>
	</div>
	<div class="navbar-center hidden lg:flex">
		<ul class="menu menu-horizontal px-1">
			<li><a href="/">Home</a></li>
			<li><a href="/overview">View Data</a></li>
			<li><a href="/downloads">Downloads</a></li>
		</ul>
	</div>
	<div class="navbar-end mr-2">
		<a class="btn btn-ghost"
			>Publication<svg
				xmlns="http://www.w3.org/2000/svg"
				width="15"
				height="15"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="feather feather-external-link"
				><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline
					points="15 3 21 3 21 9"
				></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg
			></a
		>
	</div>
</div>
