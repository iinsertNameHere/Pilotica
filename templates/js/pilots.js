// Function to delete a pilot from the DB
function delete_pilot(id) {
    fetch("{{ url_for('service.pilot') }}?id="+id, {method: 'DELETE'})
    .then(response => response.text())
    .then(data => new Transport(data).load())
    .then(result => {
        if (result != "OK") {
            alert("Failed!")
            return
        }
        window.location.href = "{{ url_for('webinterface.pilots') }}"
    });
}

function submit_editModal_form() {
    $('#editModal-form').submit()
}

const addPilot_pwdHtml = '\
<div class="form-group"> \
    <label for="password1" class="col-form-label">Password:</label> \
    <input type="text" form="editModal-form" class="form-control" name="password1" id="password1" required></input> \
</div> \
<div class="form-group"> \
    <label for="password2" class="col-form-label">Repeat Password:</label> \
    <input type="text" form="editModal-form" class="form-control" name="password2" id="password2" required></input> \
</div>'

const editPilot_pwdHtml = " \
<input type='checkbox' onclick='handle_check()' class='form-check-input' name='changePwd' id='changePwd' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'> \
<label for='changePwd' class='form-check-label'>New Password</label> \
<div id='form-pwds' style='display: none; margin-bottom: 10px'> \
    <div class='form-group'> \
        <label for='password1' class='col-form-label'>Password:</label> \
        <input type='text' class='form-control' name='password1' id='password1'></input> \
    </div> \
    <div class='form-group'> \
        <label for='password2' class='col-form-label'>Repeat Password:</label> \
        <input type='text' class='form-control' name='password2' id='password2'></input> \
    </div> \
</div>"

function handle_check()
{
  var checkbox = document.getElementById('changePwd');
  if (checkbox.checked == true)
  {
    document.getElementById('form-pwds').style.display = "block"
  } else {
    document.getElementById('form-pwds').style.display = "none"
  }
}

function add_pilot() {
    var modal = $('#editModal')

    modal.find('.modal-title').text("New Pilot")
    document.getElementById('editModal-form').action = "{{ url_for('webinterface.new_pilot') }}"

    $('#pwd-group').html(addPilot_pwdHtml)
    $('#editModal').modal('show')
}

function edit_pilot(id) {
    var modal = $('#editModal')

    modal.find('.modal-title').text("Editing Pilot "+id)
    document.getElementById('editModal-form').action = "{{ url_for('webinterface.edit_pilot') }}"
    $('#pwd-group').html(editPilot_pwdHtml)
    
    fetch("{{ url_for('service.pilot') }}?id="+id, {method: 'GET'})
    .then(response => response.text())
    .then(data => new Transport(data).load())
    .then(result => {
        if (result == "FAILED") {
            alert("Failed!")
            return
        }
        jdata = JSON.parse(result)
        document.getElementById('pilot_id').value = parseInt(id)
        document.getElementById('name').value = jdata['name']
        document.getElementById('role').value = jdata['role']
        if ('{{ current_pilot.id }}' == id) {
            document.getElementById('role').disabled = "true"
        }
    })

    $('#editModal').modal('show')
}

const original_dialogHtml = document.getElementById('editModal').innerHTML

function close_dialog() {
    $('#editModal').html(original_dialogHtml)
    $('#editModal').modal('hide')
}