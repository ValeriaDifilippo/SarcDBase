document.addEventListener('DOMContentLoaded', () => {
    const subsectionSelect = document.getElementById('subsection');
    const subsectionContent = document.getElementById('subsection-content');

    subsectionSelect.addEventListener('change', async () => {
        const subsection = subsectionSelect.value;
        const response = await fetch(`/subsection/${subsection}`);
        const content = await response.text();
        subsectionContent.innerHTML = content;
    });

    // Trigger change event on page load to load the initial subsection
    subsectionSelect.dispatchEvent(new Event('change'));
});
