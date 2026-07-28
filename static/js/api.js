function __buildTable(data) {
    const people_data = document.getElementById('people-data');
    
    for(let i = 0; i < data.length; i++) {

        const tr = document.createElement('tr');
        
        const td1 = document.createElement('td');
        const td2 = document.createElement('td');
        const td3 = document.createElement('td');
        const td4 = document.createElement('td');
                
        td1.innerText = data[i].id;
        td2.innerText = data[i].first_name;
        td3.innerText = data[i].last_name;
        td4.innerText = data[i].email;
        
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3);
        tr.appendChild(td4);
                
        people_data.appendChild(tr);
    }
}

function __init() {

    fetch('/people')
        .then(resp => {
            if(!resp.ok) {
                throw Error('Server connection error');
            }
            return resp.json();
        })
        .then(data => {
            __buildTable(data);
        })
        .catch(error => {
            console.error(error);
        });
}


__init();

function putEmail(id, newEmail) {
    fetch(`/people/${id}/email`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: newEmail })
    })
    .then(resp => {
        if (!resp.ok) throw Error('Erro ao atualizar e-mail');
        return resp.json();
    })
    .then(data => {
        console.log('E-mail atualizado com sucesso:', data);
    })
    .catch(error => console.error(error));
}

function deletePerson(id) {
    fetch(`/people/${id}`, {
        method: 'DELETE'
    })
    .then(resp => {
        if (!resp.ok) throw Error('Erro ao deletar pessoa');
        return resp.json();
    })
    .then(data => {
        console.log('Registro deletado com sucesso:', data);
    })
    .catch(error => console.error(error));
}

function updatePerson(id, updatedFields) {
    fetch(`/people/${id}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedFields)
    })
    .then(resp => {
        if (!resp.ok) throw Error('Erro ao atualizar dados');
        return resp.json();
    })
    .then(data => {
        console.log('Dados atualizados com sucesso:', data);
    })
    .catch(error => console.error(error));
}