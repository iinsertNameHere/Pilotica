// Class to interact with the Transport class from Python
class Transport {
    constructor(data) {
        this.data = data
    }

    // Load transported data
    load() {
        return fetch("{{ url_for('transport_load') }}?data="+this.data, {method: 'GET'}).then(response => response.text())
    }

    // Dump data to transport
    dump() {
        return fetch("{{ url_for('transport_dump') }}?data="+this.data, {method: 'GET'}).then(response => response.text())
    }
}

// Funtion to use a Confirmation dialog when deleting something
function confirm_delete(func, id=NaN) {
    // Show dialog
    $('#deleteModal').modal('show');

    // Set onclick function
    $('#deleteButton').on('click', function() {
        if (id != NaN) {
            func(id)
        }
        else {
            func()
        }
        $('#deleteModal').modal('hide');
    });
}