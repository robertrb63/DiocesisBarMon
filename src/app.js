
import './App.css';

import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [usuarios, setUsuarios] = useState([]);
  const [busqueda, setBusqueda] = useState("");

  
  useEffect(() => {
  axios.get("http://127.0.0.1:8000/api/usersdb/")
    .then(response => {
      console.log(response.data); // Para depurar
      setUsuarios(response.data);
    })
    .catch(error => {
      console.error("Error al obtener los usuarios:", error);
    });
}, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>Lista de Usuarios</h1>
      {usuarios.length === 0 ? (
        <p>No hay usuarios disponibles.</p>
      ) : (
        <table border="1" cellPadding="8" style={{ borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Teléfono</th> 
              <th>Email</th>
              <th>Población</th>
              <th>Grupo Parroquial</th>
              <th>Unidad</th>
              <th>Moderador</th>
              <th>Tel. Moderador</th>
              <th>Arciprestazgo</th>
              <th>Arcipreste</th>
              <th>Tel. Arciprestazgo</th>
              <th>Animador</th>
              <th>Tel. Animador</th>
            </tr>
          </thead>
          <tbody>
            {usuarios
  .filter(user =>
    user.grupo_parroquial.toLowerCase().includes(busqueda.toLowerCase())
  )
  .map((user, index) => (
    <tr key={index}>
      <td>{user.nombre}</td>
      <td>{user.telefono}</td>
      <td>{user.email}</td>
      <td>{user.poblacion}</td>
      <td>{user.grupo_parroquial}</td>
      <td>{user.unidad}</td>
      <td>{user.moderador}</td>
      <td>{user.tel_moderador}</td>
      <td>{user.arciprestazgo}</td>
      <td>{user.arcipreste}</td>
      <td>{user.tel_arciprestazgo}</td>
      <td>{user.animador}</td>
      <td>{user.tel_animador}</td>
    </tr>
))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;
