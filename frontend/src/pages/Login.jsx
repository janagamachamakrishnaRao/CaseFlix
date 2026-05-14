import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

export default function Login() {

  const navigate = useNavigate();

  const [isRegister, setIsRegister] = useState(false);

  const [formData, setFormData] = useState({
    username: "",
    password: ""
  });

  const submitAuth = async () => {

    const endpoint = isRegister
      ? "register"
      : "login";

    try {

      const response = await fetch(
        `https://caseflix-backend.onrender.com/${endpoint}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(formData)
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail);
        return;
      }

      if (!isRegister) {

        localStorage.setItem(
          "token",
          data.access_token
        );

        localStorage.setItem(
          "username",
          data.username
        );

        navigate("/");

      } else {

        alert("Registration successful");

        setIsRegister(false);
      }

    } catch (error) {

      console.error(error);

    }
  };

  return (

    <div className="authPage">

      <div className="authCard">

        <h1>CaseFlix AI</h1>

        <h2>
          {isRegister ? "Create Account" : "Login"}
        </h2>

        <input
          type="text"
          placeholder="Username"
          value={formData.username}
          onChange={(e) =>
            setFormData({
              ...formData,
              username: e.target.value
            })
          }
        />

        <input
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={(e) =>
            setFormData({
              ...formData,
              password: e.target.value
            })
          }
        />

        <button onClick={submitAuth}>

          {isRegister ? "Register" : "Login"}

        </button>

        <p
          className="switchAuth"
          onClick={() => setIsRegister(!isRegister)}
        >

          {
            isRegister
              ? "Already have an account? Login"
              : "Create new account"
          }

        </p>

      </div>

    </div>
  );
}