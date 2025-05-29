<script lang="ts">

    type File = {
      title: string;
      description: string;
      download: string;
    };

    let { files }: {files: File[]} = $props();

//   export let files: File[] = [
//     {
//       title: "Sample File 1",
//       description: "This is a description for the first file.",
//       download: "https://example.com/file1.zip"
//     },
//     {
//       title: "Sample File 2",
//       description: "This is a description for the second file.",
//       download: "https://example.com/file2.zip"
//     }
//   ];
</script>

<div class="container mx-auto px-4 py-8 space-y-4">
  <h1 class="text-3xl font-bold text-center mb-6">Downloads</h1>

  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
    {#each files as file}
      <div class="card bg-base-100 outline outline-1 outline-gray-200 shadow-lg hover:shadow-xl transition-shadow duration-300">
        <div class="card-body">
          <h2 class="card-title">{file.title}</h2>
          <p>{file.description}</p>
          <div class="card-actions">
            <a href={file.download} class="btn btn-primary btn-block" download>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-download"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg> Download
            </a>
          </div>
        </div>
      </div>
    {/each}
  </div>
</div>
