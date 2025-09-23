document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('compare-form');
    const sliders = form.querySelectorAll('input[type="range"]');
    const resultsDiv = document.getElementById('results');

    // Update display value on slider input
    sliders.forEach(slider => {
        const valueSpan = document.getElementById(`${slider.id}-value`);
        if (valueSpan) {
            valueSpan.textContent = slider.value;
            slider.addEventListener('input', () => {
                valueSpan.textContent = slider.value;
            });
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        resultsDiv.innerHTML = '<p>Comparaison en cours...</p>';

        const data = {
            "HOSPITALISATION": {
                "honoraires_chirurgien_optam": document.getElementById('honoraires_chirurgien_optam').value + " % BR",
                "chambre_particuliere": document.getElementById('chambre_particuliere').value + " €"
            },
            "SOINS_COURANTS": {
                "consultation_generaliste_optam": document.getElementById('consultation_generaliste_optam').value + " % BR"
            },
            "DENTAIRE": {
                "soins_dentaires": document.getElementById('soins_dentaires').value + " % BR",
                "implantologie": document.getElementById('implantologie').value + " €",
                "orthodontie": document.getElementById('orthodontie').value + " % BR"
            },
            "OPTIQUE": {
                "verres_complexes": document.getElementById('verres_complexes').value + " €"
            }
        };

        try {
            const response = await fetch('/compare', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }

            displayResults(result.table);

        } catch (error) {
            resultsDiv.innerHTML = `<p>Une erreur est survenue: ${error.message}</p>`;
            console.error('There was a problem with the fetch operation:', error);
        }
    });

    function displayResults(data) {
        if (!data) {
            resultsDiv.innerHTML = '<p>Aucune réponse du modèle.</p>';
            return;
        }

        resultsDiv.innerHTML = marked.parse(data);
    }
}); 