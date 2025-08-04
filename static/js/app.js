async function cargarCandidatos() {
    const lista = document.getElementById("lista-candidatos");
    lista.innerHTML = "Cargando.";

    try {
        const res = await fetch("http://127.0.0.1:5000/api/candidatos");

        const data = await res.json();

        lista.innerHTML = "";
        data.forEach(c => {
            const item = document.createElement("li");
            item.textContent = `${c.nombre} - ${c.email} - ${c.telefono}`;
            lista.appendChild(item);
        });

        if (data.length === 0) {
            lista.innerHTML = "<li>No hay candidatos procesados aún.</li>";
        }

    } catch (error) {
        console.error(error);
        lista.innerHTML = "<li>Error al cargar los candidatos.</li>";
    }
}
