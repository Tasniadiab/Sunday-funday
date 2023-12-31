import { useState, useEffect } from "react";
import { Modal, Button, Spinner } from "react-bootstrap";
import { NavLink, useNavigate } from "react-router-dom";
import useToken from "@galvanize-inc/jwtdown-for-react";

function LoginForm({ handleSignupFromLogin, handleLoginClose }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isError, setIsError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login, token } = useToken();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    await login(username, password);

    setTimeout(() => {
      setIsLoading(false);
      if (token === null) {
        setIsError(true);
        setErrorMessage(
          "Oops! The username or password you entered is incorrect. Please double-check and try again."
        );
        setPassword("");
      } else {
        setUsername("");
        setPassword("");
      }
    }, 500);
  };

  let errorClass = "alert alert-danger d-none";

  if (isError) {
    errorClass = "alert alert-danger";
  }

  const handleInputChange = (e, setter) => {
    setIsError(false);
    setter(e.target.value);
  };

  const handlePasswordToggle = () => {
    setShowPassword(!showPassword);
  };

  useEffect(() => {
    if (token !== null) {
      handleLoginClose();
      navigate("/dashboard");
    }
  }, [token, navigate, handleLoginClose]);

  return (
    <>
      <Modal.Header closeButton>
        <Modal.Title>Login</Modal.Title>
      </Modal.Header>
      <Modal.Body className="">
        <form onSubmit={(e) => handleSubmit(e)}>
          <div className="mb-3">
            <label className="form-label">Email</label>
            <input
              name="username"
              value={username}
              type="text"
              className="form-control"
              onChange={(e) => handleInputChange(e, setUsername)}
            />
          </div>
          <div className="mb-3">
            <label className="form-label">Password</label>
            <div className="input-group">
              <input
                name="password"
                value={password}
                type={showPassword ? "text" : "password"}
                className="form-control"
                onChange={(e) => handleInputChange(e, setPassword)}
              />
              <button
                className="btn btn-outline-secondary"
                type="button"
                onClick={handlePasswordToggle}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>
          <Modal.Footer>
            {isLoading ? (
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
            ) : (
              <div className={errorClass}>{errorMessage}</div>
            )}
            <Button variant="danger" onClick={handleLoginClose}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" value="Login">
              Login
            </Button>
          </Modal.Footer>
        </form>
        <NavLink onClick={handleSignupFromLogin}>Sign Up Instead</NavLink>
      </Modal.Body>
    </>
  );
}

export default LoginForm;
