import React, { useState } from "react";
import axios from "../axiosConfig";

type AddUserModalProps = {
  onClose: () => void;
  onUserAdded: () => void; // Callback to refresh the user list
};

const AddUserModal: React.FC<AddUserModalProps> = ({ onClose, onUserAdded }) => {
  const [username, setUsername] = useState<string>("");
  const [age, setAge] = useState<number | "">("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post("/user/add", { username, age });
      onUserAdded();
      onClose();
    } catch (error) {
      console.error("Error adding user:", error);
    }
  };

  return (
    <div
      className="modal show d-block"
      tabIndex={-1}
      style={{ backgroundColor: "rgba(0, 0, 0, 0.5)" }}
    >
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Add User</h5>
            <button
              type="button"
              className="btn-close"
              onClick={onClose}
            ></button>
          </div>
          <div className="modal-body">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label" htmlFor="username">
                  Username
                </label>
                <input
                  type="text"
                  className="form-control"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="mb-3">
                <label className="form-label" htmlFor="age">
                  Age
                </label>
                <input
                  type="number"
                  className="form-control"
                  id="age"
                  value={age}
                  onChange={(e) => setAge(Number(e.target.value))}
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary">
                Add User
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddUserModal;
