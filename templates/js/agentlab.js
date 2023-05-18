function delete_binary(name) {
    fetch("{{ url_for('service.deletebin') }}?filename="+name, {
        method: 'DELETE',
    }).then(response => response.text())
    .then(data => new Transport(data).load()).then(result => {
        if (result != "OK") {
            alert("Failed!")
            return
        }
        window.location.href = "{{ url_for('webinterface.agentlab') }}"
    });
}