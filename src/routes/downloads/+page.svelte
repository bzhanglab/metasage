<script>
  import DownloadPage from '$lib/components/DownloadPage.svelte';
	import NavBar from '$lib/components/NavBar.svelte';

  const downloadData = [
    {
      title: "All Metabolite Data",
      description: "Feature importance scores per cohort for all significant metabolites.",
      download: "/downloads/all_metabolite_data.tar.xz"
    },
    {
      title: "Chart Data",
      description: "Data used to generate the charts on the overview page.",
      download: "/downloads/chart_data.tar.xz"
    }
  ];
</script>

<NavBar></NavBar>
<DownloadPage files={downloadData} />
