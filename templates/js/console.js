function delete_task(id) {
    fetch("{{ url_for('service.task') }}?id="+id, {
        method: 'DELETE',
        headers: {"key": "{{ secret_key }}"}
    }).then(response => response.text())
    .then(data => new Transport(data).load()).then(result => {
        if (result != "OK") {
            alert("Failed!")
            return
        }
        window.location.href = window.location.href
    });
}