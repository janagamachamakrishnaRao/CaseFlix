import "../App.css";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";


export default function Home() {

  const [file, setFile] = useState(null);
  const [files, setFiles] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [department, setDepartment] = useState("");
  const [location, setLocation] = useState("");

  const groupedDepartments = files.reduce((acc, item) => {

  const dept =
    item.metadata?.department || "Other";

  if (!acc[dept]) {
    acc[dept] = [];
  }

  acc[dept].push(item);

  return acc;

}, {});

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

      const response = await fetch("http://127.0.0.1:8000/files");

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
  `http://127.0.0.1:8000/search/${query}`
);
      

      const data = await response.json();

      setFiles(data.results);

    } catch (error) {
      console.error(error);
    }
  };

  // FILE UPLOAD
  const uploadFile = async () => {

    if (!file || !department || !location) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();

    formData.append("file", file);
    formData.append("department", department);
    formData.append("location", location);

    try {

      const response = await fetch("http://127.0.0.1:8000/upload", {
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

          <label className="customFileUpload">

            Choose File

            <input
              type="file"
              hidden
              onChange={(e) => setFile(e.target.files[0])}
            />

          </label>

          <span className="selectedFileName">

            {file ? file.name : "No file chosen"}

          </span>
          <select
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="search"
                >

                  <option value="">Department</option>

                  <option value="CRFS">CRFS</option>

                  <option value="CRSS">CRSS</option>

                  <option value="ICD">ICD</option>

                  <option value="RAILWAY">RAILWAY</option>

                  <option value="SOPS">SOPS</option>

                  <option value="NEW SOPS">NEW SOPS</option>

                  <option value="APPROVAL SOP">
                    APPROVAL SOP
                  </option>

                </select>

                <input
                  type="text"
                  placeholder="Location"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="search"
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

     {/* OTT DEPARTMENT ROWS */}
      <div className="rows">

        {Object.entries(groupedDepartments).map(
          ([department, deptFiles]) => (

            <div className="row" key={department}>

              <h2>{department}</h2>

              <div className="cards">

                {deptFiles.map((item, index) => (

                  <div
                    className="card intelligentCard"
                    key={index}
                    onClick={() =>
                      navigate(`/case/${item.filename}`)
                    }
                  >

                    {/* TOP */}
                      <div className="cardTop">

                        <div className="cardMenu">

                          <button
                            className="menuBtn"
                            onClick={(e) => {

                              e.stopPropagation();

                              const action = prompt(
                                "Type: rename or delete"
                              );

                              // DELETE
                              if (action === "delete") {

                                fetch(
                                  `http://127.0.0.1:8000/delete/${item.filename}`,
                                  {
                                    method: "DELETE"
                                  }
                                )
                                .then(() => fetchFiles());

                              }

                              // RENAME
                              if (action === "rename") {

                                const newName = prompt(
                                  "Enter new filename"
                                );

                                if (!newName) return;

                                fetch(
                                  `http://127.0.0.1:8000/rename/${item.filename}`,
                                  {
                                    method: "PUT",
                                    headers: {
                                      "Content-Type":
                                        "application/json"
                                    },
                                    body: JSON.stringify({
                                      new_filename: newName
                                    })
                                  }
                                )
                                .then(() => fetchFiles());

                              }

                            }}
                          >
                            ⋮
                          </button>

                        </div>

                      </div>

                    {/* PDF */}
                    <div className="previewArea">

                      <iframe
                        src={`http://127.0.0.1:8000/uploads/${item.filename}`}
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
                        📍 {
                          item.metadata?.location ||
                          "Unknown Location"
                        }
                      </p>

                    </div>

                  </div>

                ))}

              </div>

            </div>

          )
        )}

      </div>

    </div>
  );
}