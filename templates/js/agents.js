// Function to delete a agent from the DB
function delete_agent(id) {
    fetch("{{ url_for('service.agent') }}?id="+id, {
        method: 'DELETE',
    }).then(response => response.text())
    .then(data => new Transport(data).load()).then(result => {
        if (result != "OK") {
            alert("Failed!")
            return
        }
        window.location.href = "{{ url_for('webinterface.agents') }}"
    });
}

// Function to delete all agents from the DB
function delete_all() {
    fetch("{{ url_for('service.agents') }}", {
        method: 'DELETE',
    }).then(response => response.text())
    .then(data => new Transport(data).load()).then(result => {
        if (result != "OK") {
            alert("Failed!")
            return
        }
        window.location.href = "{{ url_for('webinterface.agents') }}"
    });
}