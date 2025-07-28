<script lang="ts">

	function levenshtein(s: string, t: string): number {
		if (s === t) {
			return 0;
		}
		const n = s.length;
		const m = t.length;
		if (n === 0 || m === 0) {
			return n + m;
		}
		let x = 0;
		let y: number;
		let a: number;
		let b: number;
		let c: number;
		let d: number;
		let g: number;
		let h = 0;
		const p = new Uint16Array(n);
		const u = new Uint32Array(n);
		for (y = 0; y < n; ) {
			u[y] = s.charCodeAt(y);
			p[y] = ++y;
		}

		for (; x + 3 < m; x += 4) {
			const e1 = t.charCodeAt(x);
			const e2 = t.charCodeAt(x + 1);
			const e3 = t.charCodeAt(x + 2);
			const e4 = t.charCodeAt(x + 3);
			c = x;
			b = x + 1;
			d = x + 2;
			g = x + 3;
			h = x + 4;
			for (y = 0; y < n; y++) {
				a = p[y];
				if (a < c || b < c) {
					c = a > b ? b + 1 : a + 1;
				} else {
					if (e1 !== u[y]) {
						c++;
					}
				}

				if (c < b || d < b) {
					b = c > d ? d + 1 : c + 1;
				} else {
					if (e2 !== u[y]) {
						b++;
					}
				}

				if (b < d || g < d) {
					d = b > g ? g + 1 : b + 1;
				} else {
					if (e3 !== u[y]) {
						d++;
					}
				}

				if (d < g || h < g) {
					g = d > h ? h + 1 : d + 1;
				} else {
					if (e4 !== u[y]) {
						g++;
					}
				}
				p[y] = h = g;
				g = d;
				d = b;
				b = c;
				c = a;
			}
		}

		while (x < m) {
			const e = t.charCodeAt(x);
			c = x;
			d = ++x;
			for (y = 0; y < n; y++) {
				a = p[y];
				if (a < c || d < c) {
					d = a > d ? d + 1 : a + 1;
				} else {
					if (e !== u[y]) {
						d = c + 1;
					} else {
						d = c;
					}
				}
				p[y] = d;
				c = a;
			}
			h = d;
		}

		return h;
	}

	type AutocompleteProps = {
		prefix: string;
		init_items: string[];
		placeholder_text: string;
		on_search: (val: string) => void;
		custom_error_msg: string;
	};

	let dropdown: HTMLInputElement;
	let dropdown_contents: HTMLUListElement;
	let dropdown_box: HTMLLabelElement;

	const {
		prefix = 'Node',
		init_items = [],
		placeholder_text = 'Choose a node',
		on_search = (val: string) => console.log(`Selected ${val}.`),
		custom_error_msg = 'Node not found'
	}: AutocompleteProps = $props();
	let inputVal = $state('');
	let error_msg = $state('');

	let items: string[] = $state(init_items);

	export function update_items(new_items: string[]) {
		items = new_items;
	}

	const search = () => {
		dropdown_box.classList.remove('input-error');
		// check if the input value is in the list of items
		if (items.includes(inputVal)) {
			on_search(inputVal);
			error_msg = '';
		} else {
			// make input red
			dropdown_box.classList.add('input-error');
			error_msg = custom_error_msg;
		}
	};

	// function to handle item click
	function onItemClicked(item: string, force_blur = false, was_submit = false) {
		// only blur if the dropdown is not already blurred
		const is_visible =
			dropdown_contents.checkVisibility({
				// @ts-ignore
				visibilityProperty: true
			}) && dropdown_contents.style.visibility !== 'hidden';
		if (is_visible || force_blur) {
			dropdown.blur();
			dropdown_contents.blur();
		}
		inputVal = item;
	}

	let debounceTimeout: ReturnType<typeof setTimeout>;
	let filteredItems = $state(['']);

	const updatedFilteredItems = (_: string) => {
		if (inputVal.length === 0) {
			filteredItems = items.slice(0, 50);
			clearTimeout(debounceTimeout);
			return;
		}
		clearTimeout(debounceTimeout);
		debounceTimeout = setTimeout(() => {
			// Asynchronous filtering logic
			let temp = items.filter((item: string) => {
				return item.toLowerCase().includes(inputVal.toLowerCase());
			});

			// Sorting logic remains the same...
			if (temp.length > 500) {
				temp = temp.sort((a: string, b: string) => {
					// if input is blank sort by alphabetical order except for numbers
					if (Number.isNaN(Number.parseInt(a)) && Number.isNaN(Number.parseInt(b))) {
						return a.localeCompare(b);
					}
					return Number.parseInt(a) - Number.parseInt(b);
				});
			} else {
				temp = temp.sort((a: string, b: string) => {
					if (inputVal === '') {
						// if input is blank sort by alphabetical order except for numbers
						if (Number.isNaN(Number.parseInt(a)) && Number.isNaN(Number.parseInt(b))) {
							return a.localeCompare(b);
						}
						return Number.parseInt(a) - Number.parseInt(b);
					}
					return levenshtein(a, inputVal) - levenshtein(b, inputVal);
				});
			}
			filteredItems = temp.slice(0, 50);
		}, 100); // 100ms debounce time
	};

	$effect(() => {
		updatedFilteredItems(inputVal);
	});
</script>

<form
	onsubmit={(event) => {
        event.preventDefault();
		if (filteredItems.length != 0) {
			onItemClicked(filteredItems[0]);
			search();
		}
	}}
>
	<div class="p-1 bg-base-100 w-full rounded-lg">
		<div class="flex">
			<div class="join">
				<div class="dropdown join-item">
					<label
						bind:this={dropdown_box}
						class="!focus:outline-none !focus:outline-0 !focus:border-0 input input-bordered join-item flex items-center gap-2"
					>
						{prefix}:
						<input
							bind:this={dropdown}
							class="grow !focus:outline-none !focus:outline-0 !focus:border-0"
							placeholder={placeholder_text}
							bind:value={inputVal}
						/>
						<!-- error message that appears below input -->
					</label>
					<ul
						bind:this={dropdown_contents}
						tabindex="0"
						class="dropdown-content bg-white z-1 menu p-2 shadow-sm rounded-box w-full max-h-80 flex-nowrap overflow-auto"
					>
						{#each filteredItems as item}
							<li>
								<a onclick={(event) => {event.preventDefault(); onItemClicked(item, true)}}>{item}</a>
							</li>
						{/each}
						<!-- if no items display unselectable "no items message" -->
						{#if filteredItems.length === 0}
							<li><a class="text-base-400">No Items Found</a></li>
						{/if}
					</ul>
				</div>
				<button class="btn btn-outline z-10 join-item" onclick={() => search()}>Search</button>
			</div>

			<!-- hidden submit button to allow for form submission on enter keypress -->
			<button style="display: none;" type="submit">Submit</button>
		</div>
		{#if error_msg.length !== 0}
			<div class="label">
				<span class="label-text-alt text-error">{error_msg}</span>
			</div>
		{/if}
	</div>
</form>