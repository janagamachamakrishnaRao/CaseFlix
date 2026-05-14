import "../App.css";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";


export default function Home() {

  const [file, setFile] = useState(null);
  const [files, setFiles] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  const navigate = useNavigate();
  useEffect(() => {

  const token = localStorage.getItem("token");

  if (!token) {
    navigate("/login");
  }

}, []);

  // FETCH ALL FILES
  const fetchFiles = async () => {

    try {

      const response = await fetch("https://caseflix-backend.onrender.com/files");

      const data = await response.json();

      setFiles(data.files);

    } catch (error) {
      console.error(error);
    }
  };

  // AI SEMANTIC SEARCH
  const searchCases = async (query) => {

    setSearchTerm(query);

    if (!query.trim()) {
      fetchFiles();
      return;
    }

    try {

      const response = await fetch(
        `https://caseflix-backend.onrender.com/search/${query}`
      );

      const data = await response.json();

      setFiles(data.results);

    } catch (error) {
      console.error(error);
    }
  };

  // FILE UPLOAD
  const uploadFile = async () => {

    if (!file) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();

    formData.append("file", file);

    try {

      const response = await fetch("https://caseflix-backend.onrender.com/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      alert(data.message);

      fetchFiles();

    } catch (error) {
      console.error(error);
      alert("Upload failed");
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  return (
    <div className="app">

      {/* NAVBAR */}
      <div className="navbar">

        <h1 className="logo">CaseFlix</h1>

        <div className="navRight">

          <input
            type="text"
            placeholder="Search incidents..."
            className="search"
            value={searchTerm}
            onChange={(e) => searchCases(e.target.value)}
          />

          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            className="fileInput"
          />

          <button
            onClick={uploadFile}
            className="uploadBtn"
          >
            Upload
          </button>

        </div>

      </div>

      {/* HERO SECTION */}
      <div className="banner">

        <img
          src="https://images.unsplash.com/photo-1504307651254-35680f356dfd"
          alt=""
        />

        <div className="bannerOverlay">

          <h1>AI Incident Intelligence Platform</h1>

          <p>
            Enterprise-grade incident streaming and
            investigation intelligence system.
          </p>

          <button>Explore Cases</button>

        </div>

      </div>

      {/* INCIDENT CARDS */}
      <div className="rows">

        <div className="row">

          <h2>Uploaded Cases</h2>

          <div className="cards">

            {files && files.map((item, index) => (

              <div
                className="card intelligentCard"
                key={index}
                onClick={() => navigate(`/case/${item.filename}`)}
              >

                {/* TOP SECTION */}
                <div className="cardTop">

                      <div className={`severityBadge ${item.metadata?.severity || "Low"}`}>
                        {item.metadata?.severity || "Low"}
                      </div>

                  <div className="riskScore">
                  Risk {item.metadata?.risk_score || 0}%
                </div>

                </div>

                {/* PDF PREVIEW */}
                <div className="previewArea">

                  <iframe
                    src={`https://caseflix-backend.onrender.com/uploads/${item.filename}`}
                    title="preview"
                  />

                </div>

                {/* CONTENT */}
                <div className="cardContent">

                  <h3 className="pdfTitle">
                    {item.filename}
                  </h3>

                  <p className="incidentType">
                    {item.metadata?.incident_type || "Unknown"}
                  </p>

                  <p className="department">
                    {item.metadata?.department || "Unknown"}
                  </p>
  

                </div>

              </div>

            ))}

          </div>

        </div>

      </div>

    </div>
  );
}