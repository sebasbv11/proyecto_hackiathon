import { useState } from "react";

function App() {

  const [formData, setFormData] = useState({
    nombre: "",
    cedula: "",
    poliza: "",
    motivo: ""
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/emergency",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(formData)
        }
      );

      const data = await response.json();

      setResult(data);

    } catch (error) {
      console.error(error);
    }

    setLoading(false);
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0f172a",
      color: "white",
      padding: "40px",
      fontFamily: "Arial"
    }}>

      <h1 style={{
        textAlign: "center",
        marginBottom: "30px"
      }}>
        🚑 Agente de IA de emergencia
      </h1>

      <form
        onSubmit={handleSubmit}
        style={{
          maxWidth: "500px",
          margin: "0 auto",
          display: "flex",
          flexDirection: "column",
          gap: "15px"
        }}
      >

        <input
          type="text"
          name="nombre"
          placeholder="Nombre paciente"
          onChange={handleChange}
        />

        <input
          type="text"
          name="cedula"
          placeholder="Cédula"
          onChange={handleChange}
        />

        <input
          type="text"
          name="poliza"
          placeholder="Póliza"
          onChange={handleChange}
        />

        <input
          type="text"
          name="motivo"
          placeholder="Motivo emergencia"
          onChange={handleChange}
        />

        <button type="submit">
          Analizar Emergencia
        </button>

      </form>

      {
        loading &&
        <p style={{ textAlign: "center" }}>
          Analizando caso...
        </p>
      }

      {
        result && (

          <div style={{
            maxWidth: "700px",
            margin: "40px auto",
            background: "#1e293b",
            padding: "20px",
            borderRadius: "10px"
          }}>

            <h2>Resultado</h2>

            <p>
              <strong>Póliza:</strong>
              {" "}
              {result.policy_status}
            </p>

            <p>
              <strong>Cobertura:</strong>
              {" "}
              {result.coverage}
            </p>

            <p>
              <strong>Copago:</strong>
              {" "}
              ${result.copay}
            </p>

            <p>
              <strong>Preexistencias:</strong>
              {" "}
              {result.preexisting_conditions?.join(", ")}
            </p>

            <p>
              <strong>Resumen IA:</strong>
            </p>

            <p>
              {result.ai_summary}
            </p>

            <p>
              <strong>Notificaciones:</strong>
            </p>

            <ul>
              {
                result.notifications?.map((n, i) => (
                  <li key={i}>{n}</li>
                ))
              }
            </ul>

          </div>

        )
      }

    </div>
  );
}

export default App;