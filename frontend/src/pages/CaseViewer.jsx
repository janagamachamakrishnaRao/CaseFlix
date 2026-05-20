import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import "../App.css";

export default function CaseViewer() {

  const { filename } = useParams();

  const [caseData, setCaseData] = useState(null);
  const [relatedCases, setRelatedCases] = useState([]);

  // FETCH CURRENT CASE
  useEffect(() => {

    fetch("http://127.0.0.1:8000/files")
      .then((res) => res.json())
      .then((data) => {

        const found = data.files.find(
          (item) => item.filename === filename
        );

        setCaseData(found);
      });

  }, [filename]);

  // FETCH RELATED CASES
  useEffect(() => {

    fetch(`http://127.0.0.1:8000/related/${filename}`)
      .then((res) => res.json())
      .then((data) => setRelatedCases(data.related));

  }, [filename]);

  if (!caseData) {
    return <div className="loading">Loading...</div>;
  }

  return (

    <div className="viewerPage">

      {/* NAVBAR */}
      <div className="viewerNavbar">

        <h1 className="logo">CaseFlix</h1>

      </div>

      {/* MAIN CONTENT */}
      <div className="viewerContent">

        {/* PDF VIEWER */}
        <div className="pdfSection">

          <iframe
            src={`http://127.0.0.1:8000/uploads/${filename}`}
            title="PDF Viewer"
            width="100%"
            height="100%"
          />

        </div>

        {/* AI PANEL */}
        <div className="aiPanel">

          <h2>AI Intelligence</h2>

          <div className="insightCard">

            <p>
              <strong>File:</strong>
            </p>

            <span>{caseData.filename}</span>

          </div>

          <div className="insightCard">

            <p>
              <strong>Incident Type:</strong>
            </p>

            <span>
              {caseData.metadata?.incident_type}
            </span>

          </div>

          <div className="insightCard">

            <p>
              <strong>Department:</strong>
            </p>

            <span>
              {caseData.metadata?.department}
            </span>

          </div>
          <div className="insightCard">

            <p>
              <strong>Location:</strong>
            </p>

            <span>
              {caseData.metadata?.location}
            </span>

          </div>

          <div className="insightCard">

            <p>
              <strong>Severity:</strong>
            </p>

            <span>
              {caseData.metadata?.severity}
            </span>

          </div>

          <div className="insightCard">

            <p>
              <strong>Risk Score:</strong>
            </p>

            <span>
              {caseData.metadata?.risk_score}%
            </span>

          </div>

          <div className="insightCard">

            <p>
              <strong>AI Summary:</strong>
            </p>

            <span>
              {caseData.metadata?.summary}
            </span>

          </div>

          <div className="insightCard">

            <p>
              <strong>Recommendation:</strong>
            </p>

            <span>
              Immediate safety audit and preventive
              maintenance recommended.
            </span>

          </div>

        </div>

      </div>

      {/* RELATED INCIDENTS */}
      <div className="relatedSection">

        <h2>Related Incidents</h2>

        <div className="relatedGrid">

          {relatedCases.map((item, index) => (

            <div
              className="relatedCard"
              key={index}
            >

              <h3>{item.filename}</h3>

              <p>{item.metadata.incident_type}</p>

              <span>{item.metadata.department}</span>

            </div>

          ))}

        </div>

      </div>

    </div>
  );
}